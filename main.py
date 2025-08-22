from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.requests import Request

from apis.xhs_pc_apis import XHS_Apis
from xhs_utils.data_util import handle_note_info, handle_comment_info
from xhs_utils.model import AllUserNoteRequest, NodeInfoUrlRequest, NodeInfoIdRequest, SearchRequest, \
    NoteCommentsRequest


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    全局异常处理
    :param request:
    :param exc:
    :return:
    """
    return JSONResponse(
        {
            'success': False,
            'msg': "服务器内部错误",
            'data': None
        }
    )


async def request_validation_exception_handler(
        request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    捕捉422报错并进行自定义处理
    :param request:
    :param exc:
    :return:
    """
    x = exc.errors()
    return JSONResponse(
        {
            'success': False,
            'msg': "接口请求参数错误",
            'data': None
        }
    )


app = FastAPI()
app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)
xhs_apis = XHS_Apis()


@app.post('/api/v1/get_user_all_notes')
def get_user_all_notes(req: AllUserNoteRequest):
    success, msg, res_json = xhs_apis.get_user_all_notes(req.user_url, req.cookies_str, cursor=req.cursor)
    notes = res_json.get("notes", [])
    has_more = res_json.get("has_more", False)
    cursor = res_json.get("cursor", "")
    new_result = []
    for note in notes:
        tmp_note = {}
        tmp_note['note_id'] = note['note_id']
        tmp_note['title'] = note['display_title']
        tmp_note['type'] = note['type']
        tmp_note['url'] = f"https://www.xiaohongshu.com/explore/{note['note_id']}?xsec_token={note['xsec_token']}"
        tmp_note['xsec_token'] = note['xsec_token']
        new_result.append(tmp_note)
    return {
        'success': success,
        'msg': msg,
        'data': {
            'has_more': has_more,
            'cursor': cursor,
            'notes': new_result
        }
    }


@app.post('/api/v1/get_note_info_with_url')
def get_note_info_with_url(req: NodeInfoUrlRequest):
    success, msg, note_info = xhs_apis.get_note_info(req.note_url, req.cookies_str)
    note_info = note_info['data']['items'][0]
    note_info['url'] = req.note_url
    return {
        'success': success,
        'msg': msg,
        'data': handle_note_info(note_info)
    }


@app.post('/api/v1/get_note_info_with_id')
def get_note_info(req: NodeInfoIdRequest):
    note_url = f"https://www.xiaohongshu.com/explore/{req.node_id}?xsec_token={req.xsec_token}"
    success, msg, note_info = xhs_apis.get_note_info(note_url, req.cookies_str)
    note_info = note_info['data']['items'][0]
    note_info['url'] = note_url
    return {
        'success': success,
        'msg': msg,
        'data': handle_note_info(note_info)
    }


@app.post('/api/v1/search_note')
def search_some_note(req: SearchRequest):
    success, msg, notes = xhs_apis.search_some_note(req.query, req.require_num, req.cookies_str, req.sort_type_choice,
                                                    req.note_type,
                                                    req.note_time, req.note_range, req.pos_distance, req.geo)

    notes = list(filter(lambda x: x['model_type'] == "note", notes)) if success else []
    new_result = []
    for note in notes:
        tmp_note = {}
        tmp_note['note_id'] = note['id']
        tmp_note['title'] = note['note_card']['display_title']
        tmp_note['type'] = note['note_card']['type']
        tmp_note['xsec_token'] = note['xsec_token']
        tmp_note['url'] = f"https://www.xiaohongshu.com/explore/{note['id']}?xsec_token={note['xsec_token']}"
        new_result.append(tmp_note)
    return {
        'success': success,
        'msg': msg,
        'data': new_result
    }


@app.post('/api/v1/get_note_comments')
def get_note_comments(req: NoteCommentsRequest):
    success, msg, res_json = xhs_apis.get_note_out_comment(req.note_id, req.cursor, req.xsec_token, req.cookies_str)
    if not res_json:
        return {
            'success': success,
            'msg': msg,
            'data': {
                'has_more': False,
                'cursor': "",
                'comments': []
            }
        }
    comments = res_json["data"]["comments"]
    has_more = res_json.get("has_more", False)
    cursor = res_json.get("cursor", "")
    return {
        'success': success,
        'msg': msg,
        'data': {
            'has_more': has_more,
            'cursor': cursor,
            'comments': [handle_comment_info(comment) for comment in comments]
        }
    }


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app="main:app", host='0.0.0.0', port=8000, reload=True)
