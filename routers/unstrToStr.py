from .fieldGenerator import generate_pydantic_model, struct
import json

def unstructerToStr(schema, data):
    """
    Converts unstructured data to a structured format based on the given schema.
    
    Parameters:
    schema (str): The schema description.
    data (str): The unstructured data.
    
    Returns:
    dict: The structured data.
    """
    
    model, generated_json = generate_pydantic_model(schema)

    result = struct(data, model)
    
    return result

def unstructerToStrArray(schema, data):
    """
    Converts unstructured data to a structured format based on the given schema.
    
    Parameters:
    schema (str): The schema description.
    data (str): The unstructured data.
    
    Returns:
    json: The structured data.
    """

    model, generated_json = generate_pydantic_model(schema)

    merged_result = {}
    for item in data:
        structured_item = struct(item, model)
        for key, value in structured_item.model_dump().items():
            if key not in merged_result:
                merged_result[key] = []
            merged_result[key].append(value)
    
    return merged_result

if __name__ == "__main__":
    schema = "class Person: name: str, age: int, city: str"
    data = "A boy named John Doe, aged 30, lives in New York."
    structured_data = unstructerToStr(schema, data) 
    print(structured_data)

    schema = "class Person: name: str, age: int, city: str"
    data = ["A boy named John Doe, aged 30, lives in New York.", "A girl named Jane Doe, aged 25, lives in London."]
    structured_data = unstructerToStrArray(schema, data) 
    print(structured_data)