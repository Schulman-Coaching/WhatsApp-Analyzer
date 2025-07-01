#!/usr/bin/env python3
"""
WhatsApp Chat Extractor and Analyzer using MCP Tools

This script extracts WhatsApp chat data using the WhatsApp MCP server tools
and processes it for monetization opportunity analysis.
"""

import json
import os
import time
import sys
from datetime import datetime

# Import the MCP client infrastructure
from mcp_utils import use_mcp_tool, initialize_whatsapp_mcp, cleanup_mcp_connections

# Create output directory
OUTPUT_DIR = os.path.join(os.getcwd(), "WhatsApp-Analysis", "extracted_data")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Initialize metadata
metadata = {
    "extraction_started": datetime.now().isoformat(),
    "total_chats": 0,
    "total_messages": 0,
    "processed_chats": 0
}

def save_json(data, filename):
    """Save data to a JSON file with pretty formatting"""
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Data saved to {filepath}")
    return filepath

def extract_all_chats():
    """Extract all WhatsApp chats using MCP tool"""
    all_chats = []
    page = 0
    limit = 50
    more_chats = True
    
    print(f"Starting chat extraction at {datetime.now().isoformat()}")
    
    while more_chats:
        print(f"Fetching chats page {page}...")
        try:
            # Using the MCP tool to list chats
            result = use_mcp_tool(
                server_name="github.com/lharries/whatsapp-mcp",
                tool_name="list_chats",
                arguments={
                    "limit": limit,
                    "page": page,
                    "include_last_message": True,
                    "sort_by": "last_active"
                }
            )
            
            # Check if we got any chats back
            if not result:
                more_chats = False
                break
                
            # Convert the result to proper JSON if needed
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except:
                    # If it's not valid JSON, try treating it as a single object
                    result = [result]
            
            # Ensure we're dealing with a list
            if not isinstance(result, list):
                result = [result]
                
            # Add to our collection
            all_chats.extend(result)
            print(f"Found {len(result)} chats on page {page}")
            
            # If we got fewer than the limit, we're at the end
            if len(result) < limit:
                more_chats = False
                
            page += 1
            
        except Exception as e:
            print(f"Error extracting chats: {e}")
            more_chats = False
            # Save what we have so far
            if all_chats:
                save_json(all_chats, "partial_chat_list.json")
            break
    
    # Save all chats
    metadata["total_chats"] = len(all_chats)
    print(f"Extracted {len(all_chats)} total chats")
    save_json(all_chats, "all_chats.json")
    return all_chats

def extract_messages_from_chat(chat_jid, chat_name=None, max_history_hours=None):
    """Extract messages from a specific chat"""
    all_messages = []
    page = 0
    limit = 100
    more_messages = True
    
    print(f"Extracting messages from chat: {chat_name or chat_jid}")
    
    # Prepare arguments for message extraction
    args = {
        "chat_jid": chat_jid,
        "limit": limit,
        "page": page,
        "include_context": True,
        "context_before": 1,
        "context_after": 1
    }
    
    # Add time filter if specified
    if max_history_hours:
        from datetime import datetime, timedelta
        after_date = (datetime.now() - timedelta(hours=max_history_hours)).isoformat()
        args["after"] = after_date
    
    while more_messages:
        print(f"Fetching messages page {page}...")
        try:
            # Update the page number for pagination
            args["page"] = page
            
            # Call the MCP tool to get messages
            result = use_mcp_tool(
                server_name="github.com/lharries/whatsapp-mcp",
                tool_name="list_messages",
                arguments=args
            )
            
            # Check if we got any messages back
            if not result:
                more_messages = False
                break
                
            # Convert the result to proper JSON if needed
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except:
                    # If it's not valid JSON, try treating it as a single object
                    result = [result]
            
            # Ensure we're dealing with a list
            if not isinstance(result, list):
                result = [result]
                
            # Add to our collection
            all_messages.extend(result)
            print(f"Found {len(result)} messages on page {page}")
            
            # If we got fewer than the limit, we're at the end
            if len(result) < limit:
                more_messages = False
                
            page += 1
            
            # Save intermediate results every 5 pages
            if page % 5 == 0:
                save_json(all_messages, f"messages_{chat_jid.replace('@', '_')}_partial.json")
            
        except Exception as e:
            print(f"Error extracting messages: {e}")
            more_messages = False
            # Save what we have so far
            if all_messages:
                save_json(all_messages, f"messages_{chat_jid.replace('@', '_')}_partial.json")
            break
    
    print(f"Extracted {len(all_messages)} total messages from chat: {chat_name or chat_jid}")
    return all_messages

def identify_monetization_keywords(text):
    """Identify keywords related to monetization opportunities in text"""
    if not text or not isinstance(text, str):
        return {"products": [], "services": [], "marketing": []}
        
    # These are example keywords for each category - expand as needed
    product_keywords = [
        "looking for", "need to buy", "recommend", "where can I get",
        "shop", "purchase", "buy", "product", "store", "brand", "deal",
        "selling", "sale", "discount", "price", "cost", "worth", "quality",
        "apartment", "car", "house", "furniture", "electronics", "clothing",
        "food", "delivery", "order", "subscription"
    ]
    
    service_keywords = [
        "service", "help with", "looking for someone to", "hire",
        "provider", "consultant", "freelancer", "professional", "assistance",
        "caregiver", "babysitter", "plumber", "electrician", "cleaner",
        "driver", "teacher", "tutor", "coach", "trainer", "instructor",
        "lawyer", "accountant", "doctor", "therapist", "advisor",
        "repair", "install", "fix", "build", "create", "design"
    ]
    
    marketing_keywords = [
        "interested in", "love this", "hate this", "terrible experience",
        "great product", "would recommend", "would not recommend",
        "favorite", "worst", "best", "like", "dislike", "disappointed",
        "satisfied", "awesome", "amazing", "terrible", "horrible",
        "excellent", "poor", "impressive", "unimpressive", "happy with",
        "unhappy with", "review", "rating", "stars", "feedback"
    ]
    
    found_keywords = {
        "products": [],
        "services": [],
        "marketing": []
    }
    
    text_lower = text.lower()
    
    for keyword in product_keywords:
        if keyword.lower() in text_lower:
            found_keywords["products"].append(keyword)
            
    for keyword in service_keywords:
        if keyword.lower() in text_lower:
            found_keywords["services"].append(keyword)
            
    for keyword in marketing_keywords:
        if keyword.lower() in text_lower:
            found_keywords["marketing"].append(keyword)
    
    return found_keywords

def process_message_for_monetization(message):
    """Process a single message to identify monetization opportunities"""
    # Extract text content, safely handling different message formats
    if isinstance(message, dict):
        text = message.get("text", "")
        # Some messages might have the content in a different field
        if not text and "content" in message:
            text = message["content"]
    else:
        text = str(message)
    
    # Initialize result structure
    result = {
        "message_id": message.get("id", "unknown") if isinstance(message, dict) else "unknown",
        "timestamp": message.get("timestamp", "") if isinstance(message, dict) else "",
        "keywords": {},
        "monetization_indicators": {
            "product_opportunities": [],
            "service_needs": [],
            "marketing_insights": []
        }
    }
    
    # Skip processing if text is empty
    if not text:
        return result
    
    # Identify keywords in text
    keywords = identify_monetization_keywords(text)
    result["keywords"] = keywords
    
    # Process product opportunities
    if keywords["products"]:
        result["monetization_indicators"]["product_opportunities"].append({
            "type": "product_interest",
            "keywords": keywords["products"],
            "text": text,
            "confidence": len(keywords["products"]) / 10  # Simple confidence score
        })
    
    # Process service needs
    if keywords["services"]:
        result["monetization_indicators"]["service_needs"].append({
            "type": "service_need",
            "keywords": keywords["services"],
            "text": text,
            "confidence": len(keywords["services"]) / 10  # Simple confidence score
        })
    
    # Process marketing insights
    if keywords["marketing"]:
        result["monetization_indicators"]["marketing_insights"].append({
            "type": "sentiment",
            "keywords": keywords["marketing"],
            "text": text,
            "confidence": len(keywords["marketing"]) / 10  # Simple confidence score
        })
    
    return result

def process_chat_for_monetization(chat_data):
    """Process a chat to identify monetization opportunities"""
    chat_name = chat_data.get("name", "unknown")
    chat_jid = chat_data.get("jid", "unknown")
    
    print(f"Processing chat for monetization: {chat_name}")
    
    # Initialize result structure
    result = {
        "chat_id": chat_jid,
        "chat_name": chat_name,
        "message_indicators": [],
        "summary": {
            "product_opportunities": {},
            "service_needs": {},
            "marketing_insights": {}
        }
    }
    
    # Process each message in the chat
    messages = chat_data.get("messages", [])
    for message in messages:
        # Process individual message
        message_result = process_message_for_monetization(message)
        
        # Add to list of message indicators if any were found
        has_indicators = False
        for category in message_result["monetization_indicators"]:
            if message_result["monetization_indicators"][category]:
                has_indicators = True
                break
                
        if has_indicators:
            result["message_indicators"].append(message_result)
            
        # Aggregate keywords for summary
        for category in ["product_opportunities", "service_needs", "marketing_insights"]:
            for indicator in message_result["monetization_indicators"].get(category, []):
                for keyword in indicator.get("keywords", []):
                    if keyword not in result["summary"][category]:
                        result["summary"][category][keyword] = 0
                    result["summary"][category][keyword] += 1
    
    return result

def extract_and_analyze_whatsapp_data(max_chats=None, max_history_hours=None):
    """Main function to extract and analyze WhatsApp data"""
    start_time = time.time()
    
    print(f"Starting WhatsApp data extraction at {datetime.now().isoformat()}")
    print(f"Data will be saved to {os.path.abspath(OUTPUT_DIR)}")
    
    # Extract all chats
    all_chats = extract_all_chats()
    
    # Limit the number of chats to process if specified
    if max_chats and max_chats < len(all_chats):
        print(f"Limiting to {max_chats} chats out of {len(all_chats)} total chats")
        all_chats = all_chats[:max_chats]
    
    # Dataset structure
    dataset = {
        "chats": [],
        "monetization_opportunities": [],
        "metadata": metadata
    }
    
    # Process each chat
    for chat_idx, chat in enumerate(all_chats):
        chat_jid = chat.get("jid", f"unknown_{chat_idx}")
        chat_name = chat.get("name", f"unknown_{chat_idx}")
        
        print(f"Processing chat {chat_idx+1}/{len(all_chats)}: {chat_name} ({chat_jid})")
        
        # Extract messages for this chat
        messages = extract_messages_from_chat(chat_jid, chat_name, max_history_hours)
        metadata["total_messages"] += len(messages)
        
        # Add messages to chat data
        chat_data = chat.copy()
        chat_data["messages"] = messages
        
        # Save individual chat data
        save_json(chat_data, f"chat_{chat_jid.replace('@', '_')}.json")
        
        # Process for monetization opportunities
        monetization_data = process_chat_for_monetization(chat_data)
        
        # Save individual monetization data
        save_json(monetization_data, f"monetization_{chat_jid.replace('@', '_')}.json")
        
        # Add to the dataset
        dataset["chats"].append(chat_data)
        dataset["monetization_opportunities"].append(monetization_data)
        
        # Update progress
        metadata["processed_chats"] += 1
        
        # Save incremental results every 5 chats or on the last chat
        if (chat_idx + 1) % 5 == 0 or (chat_idx + 1) == len(all_chats):
            save_json(dataset, "whatsapp_data_partial.json")
            save_json(metadata, "extraction_metadata.json")
            print(f"Saved partial results after processing {chat_idx+1} chats")
    
    # Save final results
    metadata["extraction_completed"] = datetime.now().isoformat()
    metadata["extraction_duration_seconds"] = time.time() - start_time
    
    final_path = save_json(dataset, "whatsapp_data_complete.json")
    save_json(metadata, "extraction_metadata.json")
    
    # Generate an LLM-ready summary
    generate_llm_analysis_summary(dataset)
    
    print(f"Extraction complete! Processed {len(all_chats)} chats with {metadata['total_messages']} messages")
    print(f"Data saved to {os.path.abspath(final_path)}")
    print(f"Total duration: {metadata['extraction_duration_seconds']:.2f} seconds")
    
    return final_path

def generate_llm_analysis_summary(dataset):
    """Generate a summary of monetization opportunities for LLM analysis"""
    
    # Create a simplified dataset for LLM analysis
    llm_dataset = {
        "monetization_summary": {
            "product_opportunities": {},
            "service_needs": {},
            "marketing_insights": {}
        },
        "high_value_conversations": [],
        "potential_opportunities": []
    }
    
    # Aggregate all monetization indicators across chats
    for chat_data in dataset.get("monetization_opportunities", []):
        chat_name = chat_data.get("chat_name", "Unknown Chat")
        chat_id = chat_data.get("chat_id", "Unknown ID")
        
        # Aggregate keywords from summary
        for category in ["product_opportunities", "service_needs", "marketing_insights"]:
            for keyword, count in chat_data.get("summary", {}).get(category, {}).items():
                if keyword not in llm_dataset["monetization_summary"][category]:
                    llm_dataset["monetization_summary"][category][keyword] = 0
                llm_dataset["monetization_summary"][category][keyword] += count
        
        # Count indicators in this chat
        indicator_count = sum(len(chat_data.get("message_indicators", [])))
        
        # If this chat has significant indicators, add it to high value conversations
        if indicator_count > 3:  # Arbitrary threshold, adjust as needed
            llm_dataset["high_value_conversations"].append({
                "chat_name": chat_name,
                "chat_id": chat_id,
                "indicator_count": indicator_count,
                "summary": chat_data.get("summary", {})
            })
    
    # Identify top opportunities based on frequency
    for category in ["product_opportunities", "service_needs", "marketing_insights"]:
        category_data = llm_dataset["monetization_summary"][category]
        # Sort by frequency
        sorted_items = sorted(category_data.items(), key=lambda x: x[1], reverse=True)
        # Take top 10 or fewer
        top_items = sorted_items[:10]
        
        for keyword, count in top_items:
            if count > 1:  # Minimum threshold
                llm_dataset["potential_opportunities"].append({
                    "category": category,
                    "keyword": keyword,
                    "frequency": count
                })
    
    # Save the LLM-ready dataset
    save_json(llm_dataset, "llm_analysis_data.json")
    print("Generated LLM analysis summary data")
    
    return llm_dataset

def main():
    """Main entry point for script"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract and analyze WhatsApp chats for monetization opportunities")
    parser.add_argument("--max-chats", type=int, help="Maximum number of chats to process")
    parser.add_argument("--max-history", type=int, help="Maximum history in hours to extract (default: all history)")
    parser.add_argument("--mcp-endpoint", default="http://localhost:3000", help="MCP server endpoint URL")
    parser.add_argument("--mcp-connection", choices=["sse", "websocket", "stdio"], default="sse", help="MCP connection type")
    parser.add_argument("--auth-token", help="Optional authentication token for MCP server")
    args = parser.parse_args()
    
    try:
        # Initialize MCP client
        print("Initializing WhatsApp MCP client...")
        if not initialize_whatsapp_mcp(
            endpoint=args.mcp_endpoint,
            connection_type=args.mcp_connection,
            auth_token=args.auth_token
        ):
            print("ERROR: Failed to initialize WhatsApp MCP client")
            print(f"Please ensure the MCP server is running at {args.mcp_endpoint}")
            return 1
        
        print("MCP client initialized successfully")
        
        # Run the extraction
        extract_and_analyze_whatsapp_data(
            max_chats=args.max_chats,
            max_history_hours=args.max_history
        )
        
    except Exception as e:
        print(f"Error in execution: {e}")
        import traceback
        traceback.print_exc()
        # Save metadata to capture the error state
        metadata["error"] = str(e)
        metadata["error_time"] = datetime.now().isoformat()
        save_json(metadata, "extraction_metadata_error.json")
        return 1
    finally:
        # Clean up MCP connections
        print("Cleaning up MCP connections...")
        cleanup_mcp_connections()
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
