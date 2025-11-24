# agents/youtube_travel_agent.py - Additional function to add
import os
import hashlib
import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional

from dotenv import load_dotenv

# NOTE: heavy ML/LLM libraries are imported lazily inside functions
_HAS_LANGCHAIN = True
try:
    # These imports are optional and may not be available in all environments.
    from langchain_groq import ChatGroq  # type: ignore
    from langchain.text_splitter import RecursiveCharacterTextSplitter  # type: ignore
    from langchain.docstore.document import Document  # type: ignore
    from langchain_community.vectorstores import FAISS  # type: ignore
    from langchain.chains import ConversationalRetrievalChain  # type: ignore
    from langchain_google_genai import GoogleGenerativeAIEmbeddings  # type: ignore
except Exception:
    _HAS_LANGCHAIN = False

# --------- ENV ---------
load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # for Gemini embeddings

# --------- UTIL ---------
DEFAULT_LANGS = ["en", "en-US", "en-GB", "hi", "es", "fr", "de", "it", "ja", "ko", "pt", "ru", "ar"]

def _hash_text(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()

# --------- CAPTION AVAILABILITY CHECK ---------
def check_captions_available(video_id: str) -> Dict[str, any]:
    """
    Check if captions are available for a video using YouTube API
    Returns: {
        "has_captions": bool,
        "caption_languages": list,
        "has_auto_captions": bool
    }
    """
    url = "https://www.googleapis.com/youtube/v3/captions"
    params = {
        "part": "snippet",
        "videoId": video_id,
        "key": YOUTUBE_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        items = data.get("items", [])
        if not items:
            return {
                "has_captions": False,
                "caption_languages": [],
                "has_auto_captions": False
            }
        
        languages = []
        has_auto = False
        
        for item in items:
            snippet = item.get("snippet", {})
            lang = snippet.get("language", "")
            track_kind = snippet.get("trackKind", "")
            
            if lang:
                languages.append(lang)
            
            if track_kind == "ASR":  # Automatic Speech Recognition
                has_auto = True
        
        return {
            "has_captions": len(languages) > 0,
            "caption_languages": languages,
            "has_auto_captions": has_auto
        }
    
    except Exception as e:
        print(f"Caption check failed for {video_id}: {e}")
        return {
            "has_captions": False,
            "caption_languages": [],
            "has_auto_captions": False
        }

# --------- YOUTUBE SEARCH ---------
def fetch_travel_videos(
    destination: str,
    max_results: int = 6,
    order: str = "relevance",          # "date" | "rating" | "relevance" | "title" | "videoCount" | "viewCount"
    duration: str = "any",             # "any" | "short" | "medium" | "long"
    channel_id: Optional[str] = None,
    published_after: Optional[str] = None,  # RFC3339, e.g. "2024-01-01T00:00:00Z"
    prefer_with_captions: bool = True,  # NEW: prefer videos with captions
) -> List[Dict]:
    """
    Search YouTube for destination travel guides with filters.
    """
    # Increase max_results to filter for captions
    search_max = max_results * 3 if prefer_with_captions else max_results
    
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": f"{destination} travel guide",
        "type": "video",
        "maxResults": min(search_max, 50),  # YouTube API limit
        "key": YOUTUBE_API_KEY,
        "order": order,
        "safeSearch": "none",
        "videoDuration": duration if duration in {"any","short","medium","long"} else "any",
    }
    if channel_id:
        params["channelId"] = channel_id
    if published_after:
        params["publishedAfter"] = published_after

    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    items = data.get("items", [])

    videos = []
    for it in items:
        if "videoId" not in it.get("id", {}):
            continue
        vid = it["id"]["videoId"]
        sn = it["snippet"]
        
        video_info = {
            "video_id": vid,
            "title": sn.get("title", ""),
            "description": sn.get("description", ""),
            "thumbnail": sn.get("thumbnails", {}).get("high", {}).get("url") or
                         sn.get("thumbnails", {}).get("medium", {}).get("url"),
            "channel_title": sn.get("channelTitle", ""),
            "published_at": sn.get("publishedAt", "")
        }
        
        # Check caption availability if preferred
        if prefer_with_captions:
            caption_info = check_captions_available(vid)
            video_info["caption_info"] = caption_info
            
            # Prioritize videos with captions
            if caption_info["has_captions"]:
                videos.insert(0, video_info)  # Add to front
            else:
                videos.append(video_info)  # Add to end
        else:
            videos.append(video_info)
    
    # Return only the requested number
    return videos[:max_results]

# --------- CAPTIONS (NO youtube-transcript-api) ---------
def _fetch_captions_xml(video_id: str, lang: str) -> Optional[str]:
    url = f"https://video.google.com/timedtext?lang={lang}&v={video_id}"
    res = requests.get(url, timeout=30)
    if res.status_code == 200 and res.text.strip():
        return res.text
    return None

def fetch_video_captions(video_id: str, lang_candidates: Optional[List[str]] = None) -> Optional[str]:
    """
    Try multiple languages and return plain text captions, or None.
    """
    langs = lang_candidates or DEFAULT_LANGS
    for lang in langs:
        xml_text = _fetch_captions_xml(video_id, lang)
        if not xml_text:
            continue
        try:
            root = ET.fromstring(xml_text)
            chunks = []
            for t in root.findall("text"):
                if t.text:
                    chunks.append(t.text.replace("\n", " ").strip())
            if chunks:
                return " ".join(chunks)
        except ET.ParseError:
            continue
    return None

# --------- SUMMARIZATION (Groq) ---------
def summarize_captions(captions: Optional[str]) -> str:
    if not captions:
        return "❌ **Transcript not available** - Cannot generate summary without captions."
    if not _HAS_LANGCHAIN:
        return "❌ **Summarization unavailable** - missing optional ML dependencies."

    llm = ChatGroq(model="llama3-8b-8192", temperature=0.2, api_key=GROQ_API_KEY)
    prompt = (
        "You are a travel expert. Summarize the following travel video transcript into "
        "exactly 5 concise, practical bullet points (focus on places, timing, tips, costs, transit). "
        "Avoid fluff; be specific:\n\n"
        f"{captions}"
    )
    
    try:
        resp = llm.invoke(prompt)
        return getattr(resp, "content", str(resp))
    except Exception as e:
        return f"❌ **Error generating summary**: {str(e)}"

# --------- RETRIEVER (Gemini embeddings + FAISS) ---------
# We cache the retriever *by transcript hash* so repeated questions are fast.
_retriever_cache: Dict[str, any] = {}

def _build_retriever_from_text(text: str):
    if not _HAS_LANGCHAIN:
        raise RuntimeError("Retrieval functionality requires optional langchain/Gemini packages.")

    splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=200)
    docs = splitter.split_documents([Document(page_content=text)])

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=GEMINI_API_KEY,
    )
    vectordb = FAISS.from_documents(docs, embeddings)
    return vectordb.as_retriever(search_kwargs={"k": 4})

def _get_cached_retriever(captions: str):
    key = _hash_text(captions)
    if key not in _retriever_cache:
        _retriever_cache[key] = _build_retriever_from_text(captions)
    return _retriever_cache[key]

def answer_question_about_captions(captions: Optional[str], question: str) -> str:
    if not captions or not question.strip():
        return "❌ **Sorry, I couldn't find a transcript for this video.** Questions can only be answered for videos with available captions/subtitles."
    
    try:
        if not _HAS_LANGCHAIN:
            return "❌ **Q&A unavailable** - missing optional ML dependencies."

        retriever = _get_cached_retriever(captions)
        llm = ChatGroq(model="llama3-8b-8192", temperature=0.2, api_key=GROQ_API_KEY)

        chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=retriever,
            return_source_documents=False,
            verbose=False,
        )
        result = chain.invoke({"question": question, "chat_history": []})
        return result.get("answer") or result.get("result") or str(result)
    except Exception as e:
        return f"❌ **Error processing question**: {str(e)}"

# --------- BUNDLED FETCH (with caching hints for callers) ---------
def get_destination_video_data(
    destination: str,
    max_results: int = 6,
    order: str = "relevance",
    duration: str = "any",
    channel_id: Optional[str] = None,
    published_after: Optional[str] = None,
    lang_candidates: Optional[List[str]] = None,
    prefer_with_captions: bool = True,  # NEW parameter
) -> List[Dict]:
    """
    For each video: fetch captions & summary. (Q&A built on demand)
    """
    videos = fetch_travel_videos(
        destination=destination,
        max_results=max_results,
        order=order,
        duration=duration,
        channel_id=channel_id,
        published_after=published_after,
        prefer_with_captions=prefer_with_captions,
    )
    results = []
    for v in videos:
        vid = v["video_id"]
        captions = fetch_video_captions(vid, lang_candidates=lang_candidates)
        summary = summarize_captions(captions)
        
        # Add caption availability info
        result_data = {
            "video": v,
            "captions": captions,
            "summary": summary,
            "has_captions": captions is not None,
        }
        
        # Include API caption info if available
        if "caption_info" in v:
            result_data["caption_info"] = v["caption_info"]
        
        results.append(result_data)
    
    return results