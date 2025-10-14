import os
import base64
import httpx
from typing import Dict, Any, Optional

async def get_ebay_prod_token() -> str:
    app_id = os.getenv("EBAY_PROD_APP_ID")
    cert_id = os.getenv("EBAY_PROD_CERT_ID")
    if not app_id or not cert_id:
        raise ValueError("eBay API credentials not found in .env file.")

    token_url = "https://api.ebay.com/identity/v1/oauth2/token"
    credentials = f"{app_id}:{cert_id}".encode('utf-8')
    encoded_credentials = base64.b64encode(credentials).decode('utf-8')
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {encoded_credentials}",
    }
    body = {"grant_type": "client_credentials", "scope": "https://api.ebay.com/oauth/api_scope"}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(token_url, headers=headers, data=body)
            response.raise_for_status()
            return response.json()["access_token"]
        except httpx.HTTPStatusError as e:
            print(f"Error fetching eBay Token: {e.response.status_code}\n{e.response.text}")
            raise

async def search_ebay_by_keyword(
    query: str, limit: int, offset: int, min_price: Optional[float], max_price: Optional[float]
) -> Dict[str, Any]:
    try:
        token = await get_ebay_prod_token()
        url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
        headers = {"Authorization": f"Bearer {token}", "X-EBAY-C-MARKETPLACE-ID": "EBAY_US"}
        
        filter_parts = []
        if min_price is not None or max_price is not None:
            min_p, max_p = (min_price or ""), (max_price or "")
            filter_parts.append(f"price:[{min_p}..{max_p}]")
            filter_parts.append("priceCurrency:USD")
        
        params = {"q": query, "limit": limit, "offset": offset, "filter": ",".join(filter_parts)}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"eBay Keyword Search Failed: {e}")
        raise

async def search_by_image(image_b64: str, limit: int, offset: int) -> Dict[str, Any]:
    try:
        token = await get_ebay_prod_token()
        url = "https://api.ebay.com/buy/browse/v1/item_summary/search_by_image"
        headers = {
            "Authorization": f"Bearer {token}",
            "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
            "Content-Type": "application/json",
        }
        params = {"limit": limit, "offset": offset}
        payload = {"image": image_b64}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, params=params, json=payload)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"eBay Image Search Failed: {e}")
        raise