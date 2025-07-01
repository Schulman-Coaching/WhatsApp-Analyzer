#!/usr/bin/env python3
"""
WhatsApp Data Analysis with LLMs

This script demonstrates how to use the extracted WhatsApp data
with a Language Model to analyze monetization opportunities.
"""

import json
import os
import sys
import argparse
from datetime import datetime

# Default input file
DEFAULT_INPUT = "extracted_data/llm_analysis_data.json"
# Default output file
DEFAULT_OUTPUT = "extracted_data/llm_analysis_results.json"

def load_data(input_file):
    """Load the extracted WhatsApp data for analysis"""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def generate_llm_prompt(data, prompt_type="general"):
    """Generate a prompt for LLM analysis based on the data"""
    # Different prompt types for different analysis focuses
    prompt_templates = {
        "general": """
You are a business analyst specializing in identifying monetization opportunities from conversation data.
Analyze the following WhatsApp chat data to identify potential business opportunities.

The data contains:
1. Product opportunities - where people express interest in or need for products
2. Service needs - where people request or discuss services they need
3. Marketing insights - sentiment and opinions about products/services

{data_summary}

Based on this data, please provide:
1. Top 5 most promising monetization opportunities
2. For each opportunity, explain:
   - The specific need or pain point identified
   - How it could be monetized (product, service, etc.)
   - Target audience characteristics
   - Potential business model or revenue stream
3. Overall market insights from the conversations
4. Recommendations for further research or validation
""",
        "product_focus": """
You are a product development expert specializing in identifying new product opportunities from conversation data.
Analyze the following WhatsApp chat data to identify potential product ideas and opportunities.

{data_summary}

Based on this data, please provide:
1. Top 5 most promising product opportunities
2. For each product opportunity:
   - Specific user needs this product would address
   - Key features the product should have
   - Target user characteristics
   - Potential pricing model and market positioning
3. Product categories showing the most demand
4. Next steps for validating these product ideas
""",
        "service_focus": """
You are a service business consultant specializing in identifying service opportunities from conversation data.
Analyze the following WhatsApp chat data to identify potential service business opportunities.

{data_summary}

Based on this data, please provide:
1. Top 5 most promising service business opportunities
2. For each service opportunity:
   - The specific need or pain point identified
   - Service model (subscription, one-time, etc.)
   - Target customer profile
   - Potential pricing structure and revenue model
3. Service categories showing the most demand
4. Competitive advantage strategies for these services
"""
    }
    
    # Create a summary of the data for the prompt
    summary_parts = []
    
    # Add monetization summary
    summary_parts.append("## Keyword Frequencies\n")
    
    # Product opportunities
    summary_parts.append("### Product Opportunities:")
    product_keywords = data.get("monetization_summary", {}).get("product_opportunities", {})
    if product_keywords:
        keywords_sorted = sorted(product_keywords.items(), key=lambda x: x[1], reverse=True)
        for keyword, count in keywords_sorted[:10]:  # Top 10
            summary_parts.append(f"- '{keyword}': mentioned {count} times")
    else:
        summary_parts.append("- No significant product keywords found")
    
    # Service needs
    summary_parts.append("\n### Service Needs:")
    service_keywords = data.get("monetization_summary", {}).get("service_needs", {})
    if service_keywords:
        keywords_sorted = sorted(service_keywords.items(), key=lambda x: x[1], reverse=True)
        for keyword, count in keywords_sorted[:10]:  # Top 10
            summary_parts.append(f"- '{keyword}': mentioned {count} times")
    else:
        summary_parts.append("- No significant service keywords found")
    
    # Marketing insights
    summary_parts.append("\n### Marketing Insights:")
    marketing_keywords = data.get("monetization_summary", {}).get("marketing_insights", {})
    if marketing_keywords:
        keywords_sorted = sorted(marketing_keywords.items(), key=lambda x: x[1], reverse=True)
        for keyword, count in keywords_sorted[:10]:  # Top 10
            summary_parts.append(f"- '{keyword}': mentioned {count} times")
    else:
        summary_parts.append("- No significant marketing insights found")
    
    # Add potential opportunities
    summary_parts.append("\n## Potential Opportunities")
    opportunities = data.get("potential_opportunities", [])
    if opportunities:
        for opp in opportunities[:10]:  # Top 10
            category = opp.get("category", "").replace("_", " ").title()
            keyword = opp.get("keyword", "unknown")
            frequency = opp.get("frequency", 0)
            summary_parts.append(f"- {category}: '{keyword}' (frequency: {frequency})")
    else:
        summary_parts.append("- No significant opportunities identified")
    
    # Add high-value conversations
    summary_parts.append("\n## High-Value Conversations")
    conversations = data.get("high_value_conversations", [])
    if conversations:
        for i, conv in enumerate(conversations[:5]):  # Top 5
            chat_name = conv.get("chat_name", "Unknown Chat")
            summary_parts.append(f"\n### Conversation {i+1}: {chat_name}")
            
            # Add summary for this conversation
            for category in ["product_opportunities", "service_needs", "marketing_insights"]:
                cat_display = category.replace("_", " ").title()
                keywords = conv.get("summary", {}).get(category, {})
                if keywords:
                    summary_parts.append(f"\n{cat_display}:")
                    keywords_sorted = sorted(keywords.items(), key=lambda x: x[1], reverse=True)
                    for keyword, count in keywords_sorted[:5]:  # Top 5
                        summary_parts.append(f"- '{keyword}': mentioned {count} times")
    else:
        summary_parts.append("- No high-value conversations identified")
    
    # Combine all parts into a single summary
    data_summary = "\n".join(summary_parts)
    
    # Generate the prompt using the template
    prompt = prompt_templates.get(prompt_type, prompt_templates["general"])
    prompt = prompt.format(data_summary=data_summary)
    
    return prompt

def simulate_llm_analysis(prompt):
    """
    Simulate LLM analysis results
    
    In a real implementation, this would send the prompt to an LLM API
    and return the response. For this demo, we'll return a simulated response.
    """
    print("Simulating LLM analysis...")
    
    # This is a placeholder for the actual LLM API call
    # In a real implementation, you would use an API like OpenAI, Anthropic, etc.
    
    # Simulated LLM response
    simulated_response = {
        "analysis_time": datetime.now().isoformat(),
        "monetization_opportunities": [
            {
                "title": "Car Insurance Comparison Service",
                "need": "Many users are asking for recommendations on car insurance providers and comparing rates.",
                "monetization_strategy": "Affiliate marketing with insurance providers or a commission-based comparison platform.",
                "target_audience": "New car owners and those looking to switch insurance providers.",
                "business_model": "Lead generation for insurance companies with commission on conversions."
            },
            {
                "title": "Local Plumbing Service Network",
                "need": "Frequent requests for plumber recommendations suggest high demand for reliable services.",
                "monetization_strategy": "Subscription-based network of vetted plumbers with booking platform.",
                "target_audience": "Homeowners in specific geographic areas represented in chats.",
                "business_model": "Monthly fee from service providers + small booking fee from customers."
            },
            {
                "title": "Children's Sports Programs",
                "need": "Parents discussing and searching for sports programs for their children.",
                "monetization_strategy": "Centralized platform for discovering and booking children's sports activities.",
                "target_audience": "Parents with school-age children.",
                "business_model": "Commission from program providers + premium listings."
            },
            {
                "title": "Property Listing Service",
                "need": "Many users looking for apartment and housing rentals in specific neighborhoods.",
                "monetization_strategy": "Property listing platform with verified listings and rental management tools.",
                "target_audience": "Property seekers and owners in the community.",
                "business_model": "Listing fees from landlords + premium features for property management."
            },
            {
                "title": "Home Furniture Recommendations",
                "need": "Users frequently asking for furniture recommendations and discussing quality/price.",
                "monetization_strategy": "Curated furniture marketplace with community reviews.",
                "target_audience": "New homeowners and those redecorating.",
                "business_model": "Affiliate commissions from furniture retailers + sponsored listings."
            }
        ],
        "market_insights": [
            "Community-based recommendations carry significant weight in purchase decisions",
            "Price sensitivity varies by category with quality prioritized for certain products",
            "Local service providers are preferred but discovery is challenging",
            "Seasonal patterns exist in certain product/service inquiries",
            "Trust signals are critical - users frequently ask about others' experiences"
        ],
        "recommendations": [
            "Conduct focused surveys on top opportunities to validate market size",
            "Analyze seasonal patterns in the data to identify timing for market entry",
            "Test monetization models with small-scale pilot programs",
            "Develop trust-building mechanisms as a core component of any platform",
            "Explore partnerships with existing businesses mentioned positively in chats"
        ]
    }
    
    return simulated_response

def main():
    """Main function to demonstrate LLM analysis workflow"""
    parser = argparse.ArgumentParser(description="Analyze WhatsApp data with LLM")
    parser.add_argument(
        "--input", 
        default=DEFAULT_INPUT,
        help=f"Input data file path (default: {DEFAULT_INPUT})"
    )
    parser.add_argument(
        "--output", 
        default=DEFAULT_OUTPUT,
        help=f"Output results file path (default: {DEFAULT_OUTPUT})"
    )
    parser.add_argument(
        "--prompt-type", 
        choices=["general", "product_focus", "service_focus"],
        default="general",
        help="Type of analysis to perform (default: general)"
    )
    parser.add_argument(
        "--show-prompt", 
        action="store_true",
        help="Show the generated LLM prompt"
    )
    args = parser.parse_args()
    
    print(f"=== WhatsApp Data Analysis with LLM ===\n")
    
    # Load the extracted data
    print(f"Loading data from {args.input}...")
    data = load_data(args.input)
    
    if not data:
        print("Failed to load data. Please run the extraction script first.")
        return 1
    
    print(f"Generating {args.prompt_type} analysis prompt...")
    prompt = generate_llm_prompt(data, args.prompt_type)
    
    if args.show_prompt:
        print("\n=== Generated LLM Prompt ===")
        print(prompt)
        print("============================\n")
    
    print("Analyzing data with LLM...")
    results = simulate_llm_analysis(prompt)
    
    # Save the results
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"Analysis results saved to {args.output}")
    
    # Display summary of results
    print("\n=== Analysis Results Summary ===")
    print(f"Analysis completed at: {results.get('analysis_time', 'unknown')}")
    print("\nTop Monetization Opportunities:")
    for i, opp in enumerate(results.get("monetization_opportunities", []), 1):
        print(f"{i}. {opp.get('title', 'Unknown Opportunity')}")
        print(f"   Need: {opp.get('need', 'N/A')}")
        print(f"   Strategy: {opp.get('monetization_strategy', 'N/A')}")
        print()
    
    print("Key Market Insights:")
    for insight in results.get("market_insights", []):
        print(f"- {insight}")
    
    print("\nNext Steps:")
    for rec in results.get("recommendations", []):
        print(f"- {rec}")
    print("===============================\n")
    
    print("For detailed results, refer to the output file.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
