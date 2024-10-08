from fastapi import APIRouter, File, UploadFile, HTTPException
import os 
import dotenv
from pydantic import BaseModel
from typing import Union, List, Optional

from .unstrToStr import unstructerToStr, unstructerToStrArray
from .read_file import read_pdf, read_csv, read_txt, read_html, read_excel, read_json, read_xml, read_docx, read_pptx, read_markdown
from .codeInterpreter import code_interpret, upload_file_for_code_interpreter
from .rag import rag

from firecrawl import FirecrawlApp

router = APIRouter()
dotenv.load_dotenv()

app = FirecrawlApp(api_key=os.getenv('FIRECRAWL_API_KEY'))


class Struct(BaseModel):
    schema: str
    data: Union[str, List[str]]

class Crawl(BaseModel):
    url: str
    limit: Optional[int] = 7

class Map(BaseModel):
    url: str

class Code(BaseModel):
    code: str

class UserFile(BaseModel):
    file: Union[UploadFile, str]

class RAG(BaseModel):
    docs: List[str]

@router.post("/crawl/", tags=["tools"])
async def crawl(crawl: Crawl):
    """
    Crawls a website and returns the content of the page and the content of the pages linked on the page
    """

    first_page = app.scrape_url(crawl.url)
    links = first_page['linksOnPage']
    contents = [first_page['content']]

    for link in links[:crawl.limit]:
        if link == crawl.url:
            continue
        try:
            page_content = app.scrape_url(link)['content']
            contents.append(page_content)
        except Exception as e:
            print(f"Error scraping {link}: {str(e)}")
            continue

    return contents

@router.post("/map/", tags=["tools"])
async def map(map: Map):
    return app.scrape_url(map.url)['linksOnPage']

@router.post("/struct_str/", tags=["tools"])
async def struct(struct: Struct):
    return unstructerToStr(struct.schema, struct.data)

@router.post("/struct_array/", tags=["tools"])
async def struct(struct: Struct):
    return unstructerToStrArray(struct.schema, struct.data)

@router.post("/read/", tags=["tools"])
async def read(file: UploadFile = File(...)):
    fileType = file.filename.split('.')[-1].lower()

    file_content = await file.read()

    file_readers = {
        'pdf': read_pdf,
        'csv': read_csv,
        'txt': read_txt,
        'html': read_html,
        'excel': read_excel,
        'json': read_json,
        'xml': read_xml,
        'docx': read_docx,
        'pptx': read_pptx,
        'md': read_markdown,
        'xlsx': read_excel
    }

    try:
        reader = file_readers.get(fileType)
        if reader:
            content = reader(file_content)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
    finally:
        pass
    
    return {"filename": file.filename, "content": content}


@router.post("/code/", tags=["tools"])
async def code(code: Code):
    return code_interpret(code.code)

@router.post("/file_code/", tags=["tools"])
async def file_code(file: UserFile):
    return upload_file_for_code_interpreter(file.file)

@router.post("/rag/", tags=["tools"])
async def rag(rag: RAG):
    return rag(rag.docs)