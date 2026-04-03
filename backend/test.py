from routers.detection_routes import detect_text_detailed

def test_detect_text_detailed():
    # This is a placeholder test function. In a real test, you would use a testing framework like pytest
    # and mock the dependencies of detect_text_detailed to test its behavior in isolation.
    
    # Example of how you might call the function with a sample input:
    input = "The Earth is Spherical."
    
    # Since detect_text_detailed is an async function, you would need to run it in an event
    #  loop
    import asyncio
    result = asyncio.run(detect_text_detailed(input))
    
    print(result)

if __name__ == "__main__":
    test_detect_text_detailed()