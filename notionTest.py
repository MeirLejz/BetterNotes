from notion_client import Client
import json, pdb
from openai import OpenAI

secret = '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'

# Initialize the Notion client
notion = Client(auth=secret)
openai = OpenAI()

def get_page_content(page_id):
    # Retrieve the page
    page = notion.pages.retrieve(page_id=page_id)
    
    # Get the page title
    title = page["properties"]['Name']['title'][0]['text']['content']
    
    # Retrieve all blocks for the page
    blocks = notion.blocks.children.list(block_id=page_id)

    # Save blocks as a JSON file
    with open('blocks.json', 'w') as json_file:
        json.dump(blocks, json_file, indent=4)
    
    content = []
    
    for block in blocks["results"]:
        block_type = block["type"]
        
        if block_type == "paragraph":
            text = block["paragraph"]["rich_text"][0]["plain_text"] if block["paragraph"]["rich_text"] else ""
            content.append(f"Paragraph: {text}")
        
        elif block_type == "heading_1":
            text = block["heading_1"]["rich_text"][0]["plain_text"]
            content.append(f"Heading 1: {text}")
        
        elif block_type == "heading_2":
            text = block["heading_2"]["rich_text"][0]["plain_text"]
            content.append(f"Heading 2: {text}")
        
        elif block_type == "bulleted_list_item":
            text = block["bulleted_list_item"]["rich_text"][0]["plain_text"]
            content.append(f"- {text}")
        
        elif block_type == "numbered_list_item":
            text = block["numbered_list_item"]["rich_text"][0]["plain_text"]
            content.append(f"1. {text}")
        
        elif block_type == "to_do":
            text = block["to_do"]["rich_text"][0]["plain_text"]
            checked = "✓" if block["to_do"]["checked"] else "☐"
            content.append(f"{checked} {text}")
        
        elif block_type == "image":
            url = block["image"]["file"]["url"]
            content.append(f"Image: {url}")
        
        # Add more block types as needed
    
    return title, content, blocks

# Example usage
page_id = "1234935e5ec781f8bfa4c421fb658637"
title, content, blocks = get_page_content(page_id)

# print(f"Page Title: {title}")
# print("\nContent:")
# for item in content:
#     print(item)

def add_content_to_page(page_id, content, block_id=None):
    # Create a new paragraph block
    new_block = {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": content
                    }
                }
            ]
        }
    }
    
    # Append the new block to the page
    notion.blocks.children.append(block_id=page_id, children=[new_block], after=block_id)

# Example usage
new_content = "This is a new paragraph added to the Notion page."
# add_content_to_page(page_id, new_content)

def get_chat_completion(system_prompt, user_input):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
    )
    return response.choices[0].message.content

system_prompt = "You take as input a notion block and add useful information to it."
user_input = ""
# completion = get_chat_completion(system_prompt, user_input)

for i, block in enumerate(blocks['results']):
    block_type = block['type']
    if block_type == 'paragraph':
        print(f'Block {i}')
        text = block['paragraph']['rich_text'][0]['text']['content']
        print(f'Getting completion ...')
        completion = get_chat_completion(system_prompt, text)
        print(f'Adding completion as next block ...')
        add_content_to_page(page_id, completion, block_id=block['id'])

pdb.set_trace()