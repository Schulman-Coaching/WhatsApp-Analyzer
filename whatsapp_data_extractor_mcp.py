import json
import os
import time
import sys
from datetime import datetime

# Output directory
OUTPUT_DIR = "extracted_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Metadata for tracking progress
extraction_metadata = {
    "extraction_date": datetime.now().isoformat(),
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

def extract_all_chats(callback=None):
    """Extract all available chats using pagination"""
    all_chats = []
    page = 0
    limit = 50  # Process 50 chats at a time
    
    print(f"Starting chat extraction at {datetime.now().isoformat()}")
    
    while True:
        print(f"Fetching chats page {page}...")
        try:
            # This would be executed in the actual environment that has access to the MCP tools
            response = None
            # This is where the actual MCP tool would be called
            # Example code (to be executed directly in the environment with MCP tools):
            # response = use_mcp_tool(
            #     server_name="github.com/lharries/whatsapp-mcp",
            #     tool_name="list_chats",
            #     arguments={
            #         "limit": limit,
            #         "page": page,
            #         "include_last_message": True,
            #         "sort_by": "last_active"
            #     }
            # )
            
            # For testing or when running this script directly without MCP tools
            # We simulate the response with a placeholder. This should be replaced
            # with the actual implementation when run in an environment with MCP tools
            print("IMPORTANT: This is a placeholder. Use actual MCP tools in implementation")
            if page == 0:
                # Use the known chats from our earlier test
                response = [
                    {
                        "jid": "972546720343-1594980843@g.us",
                        "name": "M3 / מ3",
                        "last_message_time": "2025-05-04T16:59:32-04:00",
                        "last_message": "I forget but was someone looking for a sports chug for their son? I have a friend doing a basketball chug if anyone is interested let me know."
                    },
                    {
                        "jid": "972542583900-1592985913@g.us",
                        "name": "Men's Team Sports RBS",
                        "last_message_time": "2025-05-04T16:52:42-04:00",
                        "last_message": "Hey everyone, this incredible chug is being done by a friend of mine and he's opening up another 2 groups for boys! Highly recommended!"
                    }
                ]
            else:
                # No more chats after the first page in this simulation
                response = []
            
            # If no more chats, break the loop
            if not response:
                break
                
            all_chats.extend(response)
            
            # If callback is provided, call it with the current progress
            if callback:
                callback(page=page, chats_found=len(all_chats))
                
            # If we got fewer chats than the limit, we've reached the end
            if len(response) < limit:
                break
                
            page += 1
            
        except Exception as e:
            print(f"Error extracting chats: {e}")
            # Save what we've got so far
            print("Saving partial chat list due to error")
            save_json(all_chats, "partial_chat_list.json")
            break
        
    extraction_metadata["total_chats"] = len(all_chats)
    print(f"Found {len(all_chats)} total chats")
    return all_chats

def extract_messages_from_chat(chat_jid, chat_name=None, max_pages=None):
    """Extract all messages from a specific chat with pagination"""
    all_messages = []
    page = 0
    limit = 100  # Process 100 messages at a time
    
    print(f"Extracting messages from chat {chat_name or chat_jid}")
    
    while True:
        print(f"Fetching messages page {page}...")
        try:
            # This would be executed in the actual environment that has access to the MCP tools
            response = None
            # This is where the actual MCP tool would be called
            # Example code (to be executed directly in the environment with MCP tools):
            # response = use_mcp_tool(
            #     server_name="github.com/lharries/whatsapp-mcp",
            #     tool_name="list_messages",
            #     arguments={
            #         "chat_jid": chat_jid,
            #         "limit": limit,
            #         "page": page,
            #         "include_context": True,
            #         "context_before": 1,
            #         "context_after": 1
            #     }
            # )
            
            # For testing or when running this script directly without MCP tools
            # Simulated placeholder response
            print("IMPORTANT: This is a placeholder. Use actual MCP tools in implementation")
            if page == 0:
                # Simulate first page of messages
                response = [
                    {
                        "id": f"msg_{chat_jid}_{page}_1",
                        "from_me": False,
                        "timestamp": "2025-05-04T16:30:00-04:00",
                        "text": f"Sample message 1 in chat {chat_name or chat_jid}",
                        "sender_phone_number": "1234567890",
                        "context_before": [
                            {"text": "Context message before"}
                        ],
                        "context_after": [
                            {"text": "Context message after"}
                        ]
                    },
                    {
                        "id": f"msg_{chat_jid}_{page}_2",
                        "from_me": True,
                        "timestamp": "2025-05-04T16:31:00-04:00",
                        "text": "I'm looking for a good insurance provider for my new car",
                        "sender_phone_number": "9876543210",
                        "context_before": [
                            {"text": "Context message before"}
                        ],
                        "context_after": [
                            {"text": "Context message after"}
                        ]
                    }
                ]
            elif page == 1:
                # Simulate second page of messages
                response = [
                    {
                        "id": f"msg_{chat_jid}_{page}_1",
                        "from_me": False,
                        "timestamp": "2025-05-04T16:32:00-04:00",
                        "text": "I can recommend XYZ Insurance, they have great rates for new cars",
                        "sender_phone_number": "1234567890",
                        "context_before": [
                            {"text": "Context message before"}
                        ],
                        "context_after": [
                            {"text": "Context message after"}
                        ]
                    },
                    {
                        "id": f"msg_{chat_jid}_{page}_2",
                        "from_me": True,
                        "timestamp": "2025-05-04T16:33:00-04:00",
                        "text": "Thanks! Do they also offer home insurance? I might bundle them",
                        "sender_phone_number": "9876543210",
                        "context_before": [
                            {"text": "Context message before"}
                        ],
                        "context_after": [
                            {"text": "Context message after"}
                        ]
                    }
                ]
            else:
                # No more messages after the second page in this simulation
                response = []
            
            # If no more messages, break the loop
            if not response:
                break
                
            all_messages.extend(response)
            
            # If we got fewer messages than the limit, we've reached the end
            if len(response) < limit:
                break
                
            # If max_pages is set, respect it
            if max_pages is not None and page + 1 >= max_pages:
                break
                
            page += 1
            
        except Exception as e:
            print(f"Error extracting messages: {e}")
            # Save what we've got so far
            print(f"Saving partial message list due to error for chat {chat_name or chat_jid}")
            save_json(all_messages, f"partial_messages_{chat_jid.replace('@', '_')}.json")
            break
    
    print(f"Found {len(all_messages)} messages in chat {chat_name or chat_jid}")
    return all_messages

def identify_monetization_keywords(text):
    """Identify keywords related to monetization opportunities in text"""
    # These are example keywords for each category
    product_keywords = [
        "looking for", "need to buy", "recommend", "where can I get",
        "shop", "purchase", "buy", "product", "store", "brand", "deal"
    ]
    
    service_keywords = [
        "service", "help with", "looking for someone to", "hire",
        "provider", "consultant", "freelancer", "professional", "assistance"
    ]
    
    marketing_keywords = [
        "interested in", "love this", "hate this", "terrible experience",
        "great product", "would recommend", "would not recommend",
        "favorite", "worst", "best", "like", "dislike"
    ]
    
    found_keywords = {
        "products": [],
        "services": [],
        "marketing": []
    }
    
    if text:
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
    # Initialize result structure
    result = {
        "message_id": message.get("id", "unknown"),
        "timestamp": message.get("timestamp"),
        "keywords": {},
        "monetization_indicators": {
            "product_opportunities": [],
            "service_needs": [],
            "marketing_insights": []
        }
    }
    
    # Extract text content
    text = message.get("text", "")
    
    # Identify keywords in text
    keywords = identify_monetization_keywords(text)
    result["keywords"] = keywords
    
    # Example simple analysis - in a real implementation, this would be more sophisticated
    # Products
    if keywords["products"]:
        result["monetization_indicators"]["product_opportunities"].append({
            "type": "product_interest",
            "keywords": keywords["products"],
            "text": text,
            "confidence": 0.7  # Placeholder confidence score
        })
    
    # Services
    if keywords["services"]:
        result["monetization_indicators"]["service_needs"].append({
            "type": "service_need",
            "keywords": keywords["services"],
            "text": text,
            "confidence": 0.7  # Placeholder confidence score
        })
    
    # Marketing
    if keywords["marketing"]:
        result["monetization_indicators"]["marketing_insights"].append({
            "type": "sentiment",
            "keywords": keywords["marketing"],
            "text": text,
            "confidence": 0.7  # Placeholder confidence score
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
        
        # Add to list of message indicators
        if any(message_result["monetization_indicators"].values()):
            result["message_indicators"].append(message_result)
            
        # Aggregate keywords for summary
        for category in ["product_opportunities", "service_needs", "marketing_insights"]:
            for indicator in message_result["monetization_indicators"].get(category, []):
                for keyword in indicator.get("keywords", []):
                    if keyword not in result["summary"][category]:
                        result["summary"][category][keyword] = 0
                    result["summary"][category][keyword] += 1
    
    return result

def main():
    """Main function to extract and process all WhatsApp chats"""
    start_time = time.time()
    
    print(f"Starting WhatsApp data extraction at {datetime.now().isoformat()}")
    print(f"Data will be saved to {os.path.abspath(OUTPUT_DIR)}")
    
    # Get all chats
    all_chats = extract_all_chats()
    
    # Save the list of chats
    save_json(all_chats, "all_chats.json")
    
    # Initialize dataset structure
    dataset = {
        "chats": [],
        "contacts": {},
        "monetization_opportunities": [],
        "metadata": extraction_metadata
    }
    
    # Process each chat
    for chat_idx, chat in enumerate(all_chats):
        chat_jid = chat.get("jid", f"unknown_{chat_idx}")
        chat_name = chat.get("name", f"unknown_{chat_idx}")
        
        print(f"Processing chat {chat_idx+1}/{len(all_chats)}: {chat_name} ({chat_jid})")
        
        # Extract all messages for this chat
        messages = extract_messages_from_chat(chat_jid, chat_name)
        extraction_metadata["total_messages"] += len(messages)
        
        # Add messages to chat data
        chat_data = chat.copy()
        chat_data["messages"] = messages
        dataset["chats"].append(chat_data)
        
        # Save individual chat data
        save_json(chat_data, f"chat_{chat_jid.replace('@', '_')}.json")
        
        # Process for monetization opportunities
        monetization_data = process_chat_for_monetization(chat_data)
        dataset["monetization_opportunities"].append(monetization_data)
        
        # Save individual monetization data
        save_json(monetization_data, f"monetization_{chat_jid.replace('@', '_')}.json")
        
        # Update progress
        extraction_metadata["processed_chats"] += 1
        
        # Save incremental results every 10 chats
        if (chat_idx + 1) % 10 == 0 or (chat_idx + 1) == len(all_chats):
            save_json(dataset, "whatsapp_data_partial.json")
            save_json(extraction_metadata, "extraction_metadata.json")
            print(f"Saved partial results after processing {chat_idx+1} chats")
    
    # Save final results
    extraction_metadata["extraction_duration_seconds"] = time.time() - start_time
    final_path = save_json(dataset, "whatsapp_data_complete.json")
    save_json(extraction_metadata, "extraction_metadata.json")
    
    print(f"Extraction complete! Processed {len(all_chats)} chats with {extraction_metadata['total_messages']} messages")
    print(f"Data saved to {os.path.abspath(final_path)}")
    print(f"Total duration: {extraction_metadata['extraction_duration_seconds']:.2f} seconds")
    
    return final_path

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error in main execution: {e}")
        import traceback
        traceback.print_exc()
