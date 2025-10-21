from .global_dict import globals

if __name__ == "__main__":
    globals["example_key"] = "example_value"
    print(f"globals['example_key'] = {globals['example_key']}")  # 输出: example_value
