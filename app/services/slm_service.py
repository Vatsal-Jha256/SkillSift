# app/services/slm_service.py
from typing import List, Optional, Dict, Any
from app.core.logging import logger
from app.core.config import settings
import requests
import json

class SLMService:
    """
    Service for interacting with a Small Language Model (SLM) 
    via the Hugging Face Inference API (using Flan-T5) 
    to generate resume improvement recommendations.
    """

    def __init__(self):
        self.api_token = settings.HF_API_TOKEN
        self.api_url = settings.HF_MODEL_API_URL
        if not self.api_token:
            logger.warning("HF_API_TOKEN environment variable not set. SLMService will not function.")
        logger.info(f"Initializing SLMService with model: {self.api_url}")

    def _build_prompt(self, resume_text: str, job_description: str, skill_gaps: List[str]) -> str:
        """Constructs a simplified prompt for the SLM to generate specific recommendations."""
        gap_str = ", ".join(skill_gaps) if skill_gaps else "None identified"
        
        # Simplified prompt: Describe the task and JSON structure clearly, without a literal template.
        prompt = f"""Context:
Resume:
{resume_text}

Job Description:
{job_description}

Identified Skill Gaps: {gap_str}

Task: Generate detailed resume improvement suggestions based ONLY on the Context (Resume, Job Description, Skill Gaps). Provide specific, actionable recommendations formatted STRICTLY as a single JSON object. 

Output Requirements:
- The output MUST be ONLY a single JSON object.
- The JSON object MUST contain ONLY the following keys: ["skill_development", "content_optimization", "keyword_enhancement", "formatting_suggestions"].
- The value for each key MUST be a list of strings, where each string is a complete, actionable recommendation.
- Provide 2-4 detailed recommendations per category.
- Focus recommendations on addressing the Identified Skill Gaps.
- For 'skill_development', suggest concrete actions (e.g., courses, projects).
- For 'content_optimization', suggest specific improvements (e.g., quantify results, use action verbs).
- For 'keyword_enhancement', list specific keywords from the Job Description to add.
- For 'formatting_suggestions', provide clear layout/consistency advice.

JSON Output:
"""
        return prompt

    def _parse_slm_response(self, generated_text: str) -> Dict[str, Any]:
        """Attempts to parse the JSON response from the SLM, expecting it after the 'JSON Output:' marker."""
        logger.debug(f"Attempting to parse SLM response. Full generated text (first 500 chars): {generated_text[:500]}...")

        # Define the marker that precedes the JSON output in our prompt
        json_marker = "JSON Output:"
        final_json = {}
        json_str = ""
        
        try:
            # Find the position *after* the marker in the full generated text
            marker_pos = generated_text.rfind(json_marker)
            
            if marker_pos == -1:
                logger.warning(f"Could not find '{json_marker}' marker in SLM response. Trying to find JSON anyway.")
                # Fallback: try finding the last '{' in the whole text
                json_start_index = generated_text.rfind('{')
                if json_start_index == -1:
                     logger.warning(f"Could not find any '{{' in SLM response: {generated_text[:200]}...")
                     return {}
                text_to_parse = generated_text[json_start_index:]
            else:
                # Start searching for JSON from the marker onwards
                text_to_parse = generated_text[marker_pos + len(json_marker):]

            # Find the start of the JSON object in the relevant text part
            json_start_index = text_to_parse.find('{')
            if json_start_index == -1:
                 logger.warning(f"Could not find '{{' after marker (or fallback start) in SLM response segment: {text_to_parse[:200]}...")
                 return {}
            
            # Adjust text_to_parse to start from the found '{'
            text_to_parse = text_to_parse[json_start_index:]

            # Find the matching closing brace for the initial opening brace
            open_brackets = 0
            json_end_index = -1
            for i, char in enumerate(text_to_parse):
                if char == '{':
                    open_brackets += 1
                elif char == '}':
                    open_brackets -= 1
                    if open_brackets == 0:
                        json_end_index = i
                        break # Found the matching closing brace
            
            if json_end_index == -1:
                logger.warning(f"Could not find matching closing '}}' for opening '{{' in SLM response segment: {text_to_parse[:200]}...")
                return {}

            # Extract the JSON string cleanly
            json_str = text_to_parse[:json_end_index + 1].strip()
            logger.debug(f"Extracted potential JSON string: {json_str}")

            # Parse the extracted JSON string
            parsed_json = json.loads(json_str)

            # Validate and structure the parsed JSON
            expected_keys = ['skill_development', 'content_optimization', 'keyword_enhancement', 'formatting_suggestions']
            if isinstance(parsed_json, dict):
                for key in expected_keys:
                    value = parsed_json.get(key)
                    if isinstance(value, list):
                        # Ensure all items in the list are strings
                        final_json[key] = [str(item) for item in value]
                    elif value is not None:
                        logger.warning(f"SLM response key '{key}' is not a list, converting: {value}")
                        final_json[key] = [str(value)] # Convert single item to list
                    else:
                        final_json[key] = [] # Add empty list if key is missing
                logger.info("Successfully parsed SLM JSON response.") # Add success log
                return final_json
            else:
                logger.warning(f"Parsed SLM response segment is not a dictionary: {parsed_json}")
                return {}

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse extracted SLM JSON segment: {e}\nExtracted segment: {json_str}\nFull generated text (first 500 chars): {generated_text[:500]}...")
            return {}
        except Exception as e:
            logger.error(f"Error during SLM response parsing: {e}\nFull generated text (first 500 chars): {generated_text[:500]}...")
            return {}

    def _build_industry_prompt(self, job_description: str) -> str:
        """Constructs a prompt for the SLM to identify the industry."""
        # Simple prompt asking for the most likely industry, removing markdown backticks
        prompt = f"""Task: Analyze the Job Description below and identify the single most likely industry it belongs to.

Job Description:
{job_description}

Instructions:
- Provide ONLY the name of the industry as a single string (e.g., "Software Development", "Healthcare", "Finance", "Marketing").
- Do not include any other text, explanations, or formatting.

Identified Industry:"""
        return prompt

    def identify_industry(self, job_description: str) -> Optional[str]:
        """Identifies the industry from a job description using the SLM."""
        if not self.api_token or not job_description:
            logger.warning("SLM token or job description missing, cannot identify industry.")
            return None

        prompt = self._build_industry_prompt(job_description)
        headers = {"Authorization": f"Bearer {self.api_token}"}
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 20, # Industry name should be short
                "temperature": 0.2, # Low temperature for focused answer
                "do_sample": False, # No sampling needed
            },
            "options": {
                "wait_for_model": True
            }
        }

        logger.info(f"Sending industry identification request to HF API: {self.api_url}")
        industry_name = None
        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=20)
            response.raise_for_status()
            api_response = response.json()
            logger.debug(f"Received industry ID response from HF API: {api_response}")

            if isinstance(api_response, list) and api_response:
                generated_text = api_response[0].get('generated_text', '')
                # Extract text after the prompt
                marker = "Identified Industry:"
                marker_pos = generated_text.rfind(marker)
                if marker_pos != -1:
                    extracted_industry = generated_text[marker_pos + len(marker):].strip()
                    # Basic cleanup (remove potential quotes, etc.)
                    industry_name = extracted_industry.strip('"\' \n	')
                    logger.info(f"Identified industry: {industry_name}")
                else:
                    logger.warning(f"Could not find '{marker}' in industry ID response: {generated_text}")
            elif isinstance(api_response, dict) and 'error' in api_response:
                logger.error(f"HF API Error (Industry ID): {api_response['error']}")
            else:
                logger.warning(f"Unexpected API response format (Industry ID): {api_response}")

        except requests.exceptions.Timeout:
             logger.error(f"HF API request timed out (Industry ID).")
        except requests.exceptions.HTTPError as e:
             logger.error(f"HF API HTTP Error (Industry ID): {e.response.status_code} - {e.response.text}")
        except Exception as e:
            logger.error(f"Unexpected error during industry identification: {e}")
            
        return industry_name

    def get_resume_recommendations(
        self, 
        resume_text: str, 
        job_description: str, 
        skill_gaps: List[str]
    ) -> Dict[str, Any]:
        """
        Generates detailed resume recommendations using the Hugging Face API.
        
        Args:
            resume_text (str): The full text of the candidate's resume.
            job_description (str): The full text of the job description.
            skill_gaps (List[str]): List of skills required by the job but missing from the resume.

        Returns:
            Dict[str, Any]: A dictionary containing structured recommendations or an empty dict if fails.
        """
        if not self.api_token:
            logger.error("Hugging Face API token not configured. Cannot get SLM recommendations.")
            return {'skill_development': [], 'content_optimization': [], 'keyword_enhancement': [], 'formatting_suggestions': [], 'general': ['Missing Hugging Face API Token.']}

        # # --- Truncation removed - Mistral has larger context window ---
        # MAX_RESUME_CHARS = 800 
        # MAX_JD_CHARS = 800     
        # 
        # truncated_resume = resume_text[:MAX_RESUME_CHARS]
        # truncated_jd = job_description[:MAX_JD_CHARS]
        # 
        # if len(resume_text) > MAX_RESUME_CHARS:
        #     logger.warning(f"Truncating resume text from {len(resume_text)} to {MAX_RESUME_CHARS} characters for SLM input.")
        # if len(job_description) > MAX_JD_CHARS:
        #      logger.warning(f"Truncating job description text from {len(job_description)} to {MAX_JD_CHARS} characters for SLM input.")
        # # --- End Truncation ---

        # Using full text now
        prompt = self._build_prompt(resume_text, job_description, skill_gaps)
        headers = {"Authorization": f"Bearer {self.api_token}"}
        payload = {
            "inputs": prompt,
            "parameters": { 
                "max_new_tokens": 500, # Keep increased length
                "temperature": 0.5, 
                "do_sample": True, # Enable sampling
            },
            "options": {
                "wait_for_model": True
            }
        }

        logger.info(f"Sending request to HF API: {self.api_url}")
        recommendations = {}
        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=45) # Increased timeout
            response.raise_for_status()
            
            api_response = response.json()
            logger.debug(f"Received response from HF API: {api_response}")
            
            if isinstance(api_response, list) and api_response:
                 generated_text = api_response[0].get('generated_text', '')
                 recommendations = self._parse_slm_response(generated_text)
            elif isinstance(api_response, dict) and 'error' in api_response:
                 logger.error(f"Hugging Face API Error: {api_response['error']}")
                 if 'estimated_time' in api_response:
                      logger.info(f"Model may be loading. Estimated time: {api_response['estimated_time']}s")
            else:
                 logger.warning(f"Unexpected API response format: {api_response}")

        except requests.exceptions.Timeout:
             logger.error(f"Hugging Face API request timed out after 45 seconds.")
        except requests.exceptions.HTTPError as e:
             logger.error(f"Hugging Face API HTTP Error: {e.response.status_code} - {e.response.text}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Hugging Face API request failed: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred during SLM interaction: {e}")

        # Ensure standard keys exist even if parsing failed or API error occurred
        final_recommendations = {k: recommendations.get(k, []) for k in ['skill_development', 'content_optimization', 'keyword_enhancement', 'formatting_suggestions']}
        if not any(final_recommendations.values()): # Add generic message if SLM fails completely
             final_recommendations["general"] = ["Could not generate detailed AI recommendations due to an SLM communication issue."]

        return final_recommendations

# Instantiate the service (optional, depending on usage pattern)
# slm_service = SLMService() 