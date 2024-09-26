from fieldGenerator import generate_pydantic_model, struct

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


if __name__ == "__main__":
    schema = "class Person: name: str, age: int, city: str"
    data = "A boy named John Doe, aged 30, lives in New York."
    structured_data = unstructerToStr(schema, data) 
    print(structured_data)