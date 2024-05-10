# longchain_example

## Installation

Install the LangChain CLI if you haven't 

```bash
pip install -U langchain-cli
```

## Install OLLAMA Locally to run models locally and pull Model 




```bash 
Install ollama from this page https://ollama.com/download 

ollama pull llama3:latest 
```

## Just to run current Model 
you can export conda environment.yml after installing and dowwloading Ollama

```bash 
conda env create -f path/to/environment.yml
```


## TO RUN
In my case I have conda environment Setup so I have to activate my environment
Note Befor running Make sure ollama is running on local system and model is download as shown in above step

```bash 
conda activate longchain    

python  app/server.py
```

## OUTPUT
Out put can been seen with POST : http://localhost:8000/llama2/prompt

Request Body Required

{
  "prompt": "string"
}

```bash 
curl -X 'POST' \
  'http://localhost:8000/llama2/prompt' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "prompt": "Why Sky is blue"
}'
```


Response :


```bash 	
Response body
Download
{
  "response": {
    "content": "The sky appears blue because of a phenomenon called Rayleigh scattering. This scattering occurs when sunlight interacts with the tiny molecules of gases in the Earth's atmosphere, such as nitrogen (N2) and oxygen (O2).\n\nHere's what happens:\n\n1. **Sunlight**: The sun emits light of all wavelengths (colors), including visible light.\n2. **Atmosphere**: When this sunlight enters the Earth's atmosphere, it encounters tiny molecules of gases like N2 and O2.\n3. **Rayleigh scattering**: These gas molecules scatter shorter-wavelength blue light more than longer-wavelength red light. This is because smaller molecules are better at scattering shorter wavelengths.\n\nAs a result, the blue light is dispersed in all directions, reaching our eyes from all parts of the sky. The combination of this scattered blue light and the direct sunlight creates the blue color we see in the sky during the daytime.\n\nHere's why other colors aren't as prominent:\n\n* **Red light**: Longer wavelengths of red light are not scattered as much by the gas molecules, so they continue to travel in a more direct path to our eyes. This is why the sun often appears yellow or orange due to the dominant red and orange components.\n* **Other colors**: The scattering effect also depends on the wavelength of the light. Green, yellow, and violet light are scattered less than blue light, which is why we don't see these colors as prominently in the sky.\n\nIn summary, the sky appears blue because of the Rayleigh scattering of sunlight by tiny gas molecules in the atmosphere, which favors shorter-wavelength blue light over longer-wavelength red light.",
    "additional_kwargs": {},
    "response_metadata": {
      "model": "llama3:latest",
      "created_at": "2024-05-10T05:51:14.505328Z",
      "message": {
        "role": "assistant",
        "content": ""
      },
      "done": true,
      "total_duration": 18897120000,
      "load_duration": 6304949708,
      "prompt_eval_count": 14,
      "prompt_eval_duration": 242487000,
      "eval_count": 328,
      "eval_duration": 12347020000
    },
    "type": "ai",
    "name": null,
    "id": "run-d605d098-cd67-4ed8-8d10-6a086a938c68-0",
    "example": false,
    "tool_calls": [],
    "invalid_tool_calls": []
  }
}
Response headers
 content-length: 2117 
 content-type: application/json 
 date: Fri,10 May 2024 05:50:55 GMT 
 server: uvicorn 
```