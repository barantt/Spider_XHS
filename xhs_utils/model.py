from typing import Optional

from pydantic import BaseModel


class AllUserNoteRequest(BaseModel):
    user_url: str
    cookies_str: str
    cursor: Optional[str] = ''


class NodeInfoUrlRequest(BaseModel):
    note_url: str
    cookies_str: str


class NodeInfoIdRequest(BaseModel):
    node_id: str
    xsec_token: str
    cookies_str: str


class SearchRequest(BaseModel):
    query: str
    cookies_str: str
    require_num: Optional[int] = 30
    sort_type_choice: Optional[int] = 0
    note_type: Optional[int] = 0
    note_time: Optional[int] = 0
    note_range: Optional[int] = 0
    pos_distance: Optional[int] = 0
    geo: Optional[str] = ''


class NoteCommentsRequest(BaseModel):
    note_id: str
    cookies_str: str
    cursor: Optional[str] = ''
    xsec_token: str
