import torch
import os
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

class LocalLLMExplainer:
    """Service for generating conversational AI explanations using a local SLM"""
    
    def __init__(self, model_id="Qwen/Qwen2.5-0.5B-Instruct"):
        self.model_id = model_id
        self.tokenizer = None
        self.model = None
        self.pipe = None
        self.is_ready = False

    def load_model(self):
        """Loads the SLM into memory (downloads to project folder on first run)"""
        try:
            # Build path to project-local model directory
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            local_model_dir = os.path.join(base_dir, 'ml', 'llm_models')
            os.makedirs(local_model_dir, exist_ok=True)

            print(f"\n============================================================")
            print(f"LOADING LOCAL AI MODEL: {self.model_id}")
            print(f"Destination: {local_model_dir}")
            print(f"Note: First run will download ~900MB data. Please wait...")
            print(f"============================================================\n")
            
            # Use CPU by default for stability on most machines, use GPU if available
            device = "cuda" if torch.cuda.is_available() else "cpu"
            
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_id, 
                cache_dir=local_model_dir
            )
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_id, 
                torch_dtype="auto", 
                device_map=device,
                cache_dir=local_model_dir
            )
            self.pipe = pipeline(
                "text-generation", 
                model=self.model, 
                tokenizer=self.tokenizer,
                device=device
            )
            self.is_ready = True
            print(f"\n✓ Local LLM Ready ({device.upper()})\n")
            return True
        except Exception as e:
            print(f"\n✗ Failed to load LLM: {e}")
            return False

    def generate_explanation(self, prediction: str, probability: float, top_factors: list) -> str:
        """Generates a conversational explanation based on model data"""
        if not self.is_ready or self.pipe is None:
            return "Local AI summary unavailable (Model still loading or failed to initialize)."

        # Format factors for the prompt
        factors_desc = []
        for f in top_factors:
            impact = "positively influenced" if f['impact'] == "Positive" else "negatively impacted"
            factors_desc.append(f"{f['factor']} which {impact} the outcome")
        
        factors_str = "; ".join(factors_desc)
        
        # Construct the prompt for Qwen-Instruct
        messages = [
            {"role": "system", "content": "You are a professional and empathetic loan officer. Your goal is to explain a loan decision to a customer based on data provided. Be concise (max 3 sentences)."},
            {"role": "user", "content": f"The loan application was {prediction} with {probability:.1%} confidence. The main reasons were: {factors_str}. Please provide a natural summary for the applicant."}
        ]

        try:
            # Generate response
            prompt = self.tokenizer.apply_chat_template(
                messages, 
                tokenize=False, 
                add_generation_prompt=True
            )
            
            outputs = self.pipe(
                prompt, 
                max_new_tokens=150, 
                do_sample=True, 
                temperature=0.7,
                top_p=0.9,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            generated_text = outputs[0]['generated_text']
            # Extract only the assistant's response
            response = generated_text.split("<|im_start|>assistant")[-1].strip()
            # Clean up potential artifacts
            response = response.replace("<|im_end|>", "").strip()
            
            return response
        except Exception as e:
            print(f"LLM Generation Error: {e}")
            return "I've analyzed your application, but encountered an error generating the natural summary. Please refer to the factor breakdown below."

# Global instance
llm_explainer = LocalLLMExplainer()
