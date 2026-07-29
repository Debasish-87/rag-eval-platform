import json
import re


class LLMResponseParser:

    REQUIRED_FIELDS = (
        "faithfulness",
        "answer_relevance",
        "hallucination",
        "reason",
    )

    @staticmethod
    def parse(response: str) -> dict:
        """
        Parse an LLM response into a validated dictionary.
        """

        response = response.strip()

        # Remove markdown code fences
        response = re.sub(r"^```(?:json)?", "", response)
        response = re.sub(r"```$", "", response)
        response = response.strip()

        # Extract first JSON object
        match = re.search(r"\{.*\}", response, re.DOTALL)

        if not match:
            raise ValueError("No JSON object found.")

        data = json.loads(match.group())

        # Validate required fields
        for field in LLMResponseParser.REQUIRED_FIELDS:
            if field not in data:
                raise ValueError(f"Missing field: {field}")

        return data

    @staticmethod
    def parse_batch(response: str) -> list[dict]:
        """
        Parse a batch LLM response into a validated list of dictionaries.
        """

        response = response.strip()

        # Remove markdown code fences
        response = re.sub(r"^```(?:json)?", "", response)
        response = re.sub(r"```$", "", response)
        response = response.strip()

        # Extract JSON array
        match = re.search(r"\[.*\]", response, re.DOTALL)

        if not match:
            raise ValueError("No JSON array found.")

        data = json.loads(match.group())

        if not isinstance(data, list):
            raise ValueError("Expected a JSON array.")

        for index, item in enumerate(data):

            if not isinstance(item, dict):
                raise ValueError(f"Item {index} is not a JSON object.")

            for field in LLMResponseParser.REQUIRED_FIELDS:
                if field not in item:
                    raise ValueError(f"Item {index} missing field: {field}")

        return data
