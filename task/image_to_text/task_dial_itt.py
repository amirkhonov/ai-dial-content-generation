import asyncio
from io import BytesIO
from pathlib import Path

from task._models.custom_content import Attachment, CustomContent
from task._utils.constants import API_KEY, DIAL_URL, DIAL_CHAT_COMPLETIONS_ENDPOINT
from task._utils.bucket_client import DialBucketClient
from task._utils.model_client import DialModelClient
from task._models.message import Message
from task._models.role import Role


async def _put_image() -> Attachment:
    file_name = 'dialx-banner.png'
    image_path = Path(__file__).parent.parent.parent / file_name
    mime_type_png = 'image/png'

    async with DialBucketClient(api_key=API_KEY, base_url=DIAL_URL) as client:
        with open(image_path, "rb") as f:
            content = BytesIO(f.read())

        print(f"Uploading {file_name}...")
        response = await client.put_file(name=file_name, mime_type=mime_type_png, content=content)
        print(f"Upload complete. URL: {response.get('url')}")

        return Attachment(
            title=file_name,
            type=mime_type_png,
            url=response.get('url')
        )


def start() -> None:
    # 1. Create DialBucketClient and upload image
    print(f"Starting image upload...")
    attachment = asyncio.run(_put_image())

    # 2. Setup models to test
    # Note: Add other models like 'claude-3-sonnet' if available in your environment
    models = ["gpt-4o"]

    for model_name in models:
        print("\n" + "="*60)
        print(f"Testing with model: {model_name}")
        print("="*60 + "\n")

        client = DialModelClient(
            endpoint=DIAL_CHAT_COMPLETIONS_ENDPOINT,
            deployment_name=model_name,
            api_key=API_KEY
        )

        message = Message(
            role=Role.USER,
            content="What do you see on this picture?",
            custom_content=CustomContent(attachments=[attachment])
        )

        try:
            response = client.get_completion(messages=[message])
            print(f"\nResponse from {model_name}:\n")
            print(response.content)
        except Exception as e:
            print(f"Error calling {model_name}: {e}")


start()
