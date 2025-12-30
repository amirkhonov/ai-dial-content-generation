import asyncio
from datetime import datetime

from task._models.custom_content import Attachment
from task._utils.constants import API_KEY, DIAL_URL, DIAL_CHAT_COMPLETIONS_ENDPOINT
from task._utils.bucket_client import DialBucketClient
from task._utils.model_client import DialModelClient
from task._models.message import Message
from task._models.role import Role

class Size:
    """
    The size of the generated image.
    """
    square: str = '1024x1024'
    height_rectangle: str = '1024x1792'
    width_rectangle: str = '1792x1024'


class Style:
    """
    The style of the generated image. Must be one of vivid or natural.
     - Vivid causes the model to lean towards generating hyper-real and dramatic images.
     - Natural causes the model to produce more natural, less hyper-real looking images.
    """
    natural: str = "natural"
    vivid: str = "vivid"


class Quality:
    """
    The quality of the image that will be generated.
     - ‘hd’ creates images with finer details and greater consistency across the image.
    """
    standard: str = "standard"
    hd: str = "hd"

async def _save_images(attachments: list[Attachment]):
    # Create DIAL bucket client
    async with DialBucketClient(api_key=API_KEY, base_url=DIAL_URL) as bucket_client:
        # Iterate through Images from attachments, download them and save them locally
        for i, attachment in enumerate(attachments):
            if attachment.url:
                image_data = await bucket_client.get_file(attachment.url)

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"generated_image_{timestamp}_{i}.png"

                with open(filename, "wb") as f:
                    f.write(image_data)
                print(f"Image saved as: {filename}")


def start() -> None:
    client = DialModelClient(
        endpoint=DIAL_CHAT_COMPLETIONS_ENDPOINT,
        deployment_name="dall-e-3",
        api_key=API_KEY
    )

    prompt = "A futuristic cityscape at sunset, with flying cars and towering skyscrapers, in a vivid and colorful style."
    message = Message(role=Role.USER, content=prompt)

    custom_fields = {
        "size": Size.square,
        "quality": Quality.hd,
        "style": Style.vivid
    }

    print(f"\nGenerating image with prompt: '{prompt}'\n")
    response = client.get_completion(messages=[message], custom_fields=custom_fields)

    # Get attachments from response and save generated images
    if response.custom_content and response.custom_content.attachments:
        print(f"\nReceived {len(response.custom_content.attachments)} image(s)\n")
        asyncio.run(_save_images(response.custom_content.attachments))
    else:
        print("No attachments found in response")

    # print("\n" + "="*60)
    # print("Testing with Google's imagegeneration@005 model")
    # print("="*60 + "\n")

    # google_client = DialModelClient(
    #     endpoint=DIAL_CHAT_COMPLETIONS_ENDPOINT,
    #     deployment_name="imagegeneration@005",
    #     api_key=API_KEY
    # )

    # google_custom_fields = {
    #     "aspectRatio": "1:1",
    #     "mode": "upscale"
    # }

    # google_response = google_client.get_completion(
    #     messages=[message],
    #     custom_fields=google_custom_fields
    # )

    # if google_response.custom_content and google_response.custom_content.attachments:
    #     print(f"\nReceived {len(google_response.custom_content.attachments)} image(s) from Google model\n")
    #     asyncio.run(_save_images(google_response.custom_content.attachments))
    # else:
    #     print("No attachments found in Google model response")


start()
