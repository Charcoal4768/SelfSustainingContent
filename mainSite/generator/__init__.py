import os

current_script_path = os.path.abspath(__file__)
parent_dir = os.path.dirname(current_script_path)
grandparent_dir = os.path.dirname(parent_dir)

class SearchTermsPrompt:
    def __init__(self, product1, product2, extra_txt="", template_path=None):
        if product1 is None or product2 is None:
            raise ValueError("Product terms cannot be None")

        self.product1 = product1
        self.product2 = product2
        self.extra_txt = extra_txt

        # Load system prompt directly on init
        default_path = os.path.join(parent_dir, "prompts", "search_terms.txt")
        path = template_path or default_path

        try:
            with open(path, "r") as f:
                self.system_prompt = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt template not found at {path}")
        
        self.message = f"""| Content: Product_1 -> {product1}, Product_2 -> {product2} | Extra Information: {extra_txt} |"""
        self.model = "gemini-2.5-flash"

    def __repr__(self):
        return f"Prompt: {self.message}"



#TODO: title promt, article prompt, etc, etc, schema not ready yet