import os
from enum import Enum
from typing import List, Set

from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

# --- Pydantic Models for Structured Output ---


class EnumStrideType(str, Enum):
    """Enumeration for the STRIDE threat categories."""

    SPOOFING = "S_Spoofing"
    TAMPERING = "T_Tampering"
    REPUDIATION = "R_Repudiation"
    INFORMATION_DISCLOSURE = "I_Information_Disclosure"
    DENIAL_OF_SERVICE = "D_Denial_of_Service"
    ELEVATION_OF_PRIVILEGE = "E_Elevation_of_Privilege"


class Threat(BaseModel):
    """Represents a single threat with its category, description, and countermeasure."""

    threat_category: EnumStrideType = Field(..., description="Type of threat (e.g., S_Spoofing)")
    threat_description: str = Field(..., description="A detailed description of the identified threat.")
    suggested_countermeasure: str = Field(..., description="A suggested action to mitigate the threat.")


class STRIDEAnalysisResponse(BaseModel):
    """The main response model for the STRIDE analysis of a component."""

    component_name: str = Field(..., description="The name of the software or system component being analyzed.")
    threats: List[Threat] = Field(..., description="A list of potential threats related to the component.")


def perform_stride_analysis(component_name: str, openai_api_key: str) -> STRIDEAnalysisResponse | None:
    """
    Perform a STRIDE threat analysis on a given component name using LangChain and OpenAI.

    Args:
        component_name: The name of the component from an architecture diagram to be analyzed.
        openai_api_key: Your OpenAI API key.

    Returns:
        A STRIDEAnalysisResponse object containing the structured threat analysis, or None if an error occurs.
    """
    model = ChatOpenAI(temperature=0.6, model="gpt-4o-mini", openai_api_key=openai_api_key)
    parser = PydanticOutputParser(pydantic_object=STRIDEAnalysisResponse)
    prompt_template = """
    You are an expert cybersecurity analyst specializing in threat modeling.
    Your task is to perform a STRIDE threat analysis on the following software component,
    which has been identified from an architecture diagram.

    Component Name:
    {component_name}

    Based on the typical function of a component with this name, please identify potential threats
    for each of the STRIDE categories (Spoofing, Tampering, Repudiation, Information Disclosure,
    Denial of Service, Elevation of Privilege).

    For each identified threat, provide a description and a suggested countermeasure.
    The component_name in your response must be exactly "{component_name}".

    {format_instructions}
    """
    prompt = ChatPromptTemplate.from_template(template=prompt_template, partial_variables={"format_instructions": parser.get_format_instructions()})
    chain = prompt | model | parser
    print(f"Requesting STRIDE analysis for component: {component_name}...")
    try:
        response = chain.invoke({"component_name": component_name})
        return response
    except Exception as e:
        print(f"An error occurred while analyzing '{component_name}': {e}")
        return None


def analyze_components(components: Set[str]) -> list[STRIDEAnalysisResponse]:
    """
    Analyze a set of components and return the STRIDE analysis results.

    Args:
        components: A set of component names to analyze.

    Returns:
        A list of STRIDEAnalysisResponse objects for each successfully analyzed component.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
        print("Please set your OpenAI API key to run this script.")
        return []
    all_results: list[STRIDEAnalysisResponse] = []
    for component in components:
        analysis_result = perform_stride_analysis(component, api_key)
        if analysis_result:
            all_results.append(analysis_result)
    return all_results
