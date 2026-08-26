tools = [
    {
        "type": "function",
        "name": "calculate",
        "description": "Evaluate mathematical expressions and return the numerical result. Use this tool whenever the user asks to calculate, solve, or evaluate a mathematical expression.",
        "parameters": {
            "type": "object",
            "properties": {
                "expr": {
                    "type": "string",
                    "description": " Expression that contains some mathematical calculations",
                },
            },
            "required": ["expr"],
            "additionalProperties": False
        },
        "strict": True
    },
    {
        "type": "function",
        "name": "explain",
        "description": "Use this tool whenever the user asks for an explanation in simple language, including after retrieving factual information from another tool.",
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "Study topic that is need to be explained by the model",
                },
            },
            "required": ["topic"],
            "additionalProperties": False
        },
        "strict": True
    },
    {
        "type": "function",
        "name": "generate_quiz",
        "description": "Create a quiz with answers on a given topic and difficulty. Use this tool whenever the user requests a quiz, test, or practice questions. Do not generate quizzes without this tool.",
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "Topic on the basis of which a quiz should be made",
                },
                "difficulty": {
                    "type": "string",
                    "enum": ["easy", "medium", "hard"],
                    "description": "Difficulty on the basis of which a quiz should be made",
                }
            },
            "required": ["topic", "difficulty"],
            "additionalProperties": False
        },
        "strict": True
    },
    {
        "type": "function",
        "name": "search_wikipedia",
        "description": "Search Wikipedia for factual information. Use this tool whenever the user explicitly asks to search or look up something on Wikipedia. Do not answer such requests from memory.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The topic or keyword to search for on Wikipedia",
                },
            },
            "required": ["query"],
            "additionalProperties": False
        },
        "strict": True
    }
]