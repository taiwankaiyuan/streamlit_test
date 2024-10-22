import streamlit as st
import pandas as pd

st.title('AI大模型應用開發(11)：採用OpenAI的Assistant API來開發')
st.markdown("""

之前都用LangChain的套件來開發，好處是可以使用各家廠商的大型語言模型，看哪一家強，就用哪一家。

但是我們也能採用OpenAI的Assistant API來開發，雖然只能使用OpenAI自己家的語言模型，但是很多功能都內建好了，用起來就不會像是LangChain這麼麻煩（但是我以為LangChain已經很方便了）。

## 讓AI幫你算數學

首先創建一個OpenAI的實例，然後調用 `.beta.assistants.create()`

來創建助手。

```python
from openai import OpenAI
client = OpenAI()

# 注意，截至2024/10/20為止，這個版本仍在測試階段
assistant = client.beta.assistants.create(
    model="gpt-3.5-turbo",
    name="數學助手",
    instructions="你是一個數學助手，可以透過編寫和運行程式來回答數學相關問題。",
    tools=[{"type": "code_interpreter"}] # 官方指定寫法
)
```

創建對話執行緒，這個執行緒將保存這次互動的上下文資料，並允許 API 在多輪互動中保持一致性。

每一個執行緒會有自己的id，可以用 `thread.id`來查驗。

```python
thread = client.beta.threads.create()
```

當我們要使用此執行緒，依照底下作法：

```python
# 創建一則來自使用者的訊息
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user", #
    content="我需要解這個方程式：`5x^2−1200x+72000=0`，未知數X應該是多少？"
)

# 創建一個運行，等一下讓AI助手依照此設定來運行程式
# 等一下呼叫run後，就會開始執行，但是不會這麼快就得到答案，可能需要排隊
run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id,
    instructions="請稱呼使用者為烏鴉大叔" # 針對此次運行提供給AI的建議
)
```

如果呼叫下列程式，可能會得到 `queued`、`in_progress`、`completed`，代表了排隊中、進行中、已完成。

```python
client.beta.threads.runs.retrieve(
    thread_id=thread.id,
    run_id=run.id
).status
```

如果狀態是已完成（completed），代表可以看AI的回應了。

我們可以寫一個while迴圈，這樣就不用手動刷新。

```python
while run.status != "completed":
    keep_retrieving_run = client.beta.threads.runs.retrieve(
        thread_id=thr
        
        ead.id,
        run_id=run.id
    )
    print(f"運行狀態：{keep_retrieving_run.status}")
    if keep_retrieving_run.status == "completed":
        break
```

查看執行緒上的所有訊息

```python
messages = client.beta.threads.messages.list(
    thread_id=thread.id
)

for data in messages.data: # messages.data是列表
    print(data.content[0].text.value)
    print("------")
```
"""
)
st.image('./image.png', use_column_width=True)

st.markdown(
"""
為了使用方便，我們可以把上述的過程全部都放到一個函數內。

```python
def get_response_from_assistant(assistant, thread, prompt, run_instruction=""):
    message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content=prompt
    )
    
    run = client.beta.threads.runs.create(
      thread_id=thread.id,
      assistant_id=assistant.id,
      instructions=run_instruction
    )
    
    while run.status != "completed":
        keep_retrieving_run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        print(f"Run status: {keep_retrieving_run.status}")

        if keep_retrieving_run.status == "completed":
            break
    
    messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )
    
    for data in messages.data:
        print("\n")
        print(data.content[0].text.value)
        print("------")
```

測試看看。

```python
get_response_from_assistant(assistant, thread, "2的56次方等於多少")
```
"""
)

st.image('./image 1.png', use_column_width=True)

st.markdown(
    """
## 讓AI讀取PDF

首先先讀取PDF檔：

底下程式要特別設定為 `”rb”`，將檔案 **論文.pdf** 以「二進位讀取模式」打開。

如果你只是打開一個純文字檔案，通常會使用 `"r"`，即「讀取模式」。但是像 PDF 這樣的檔案是二進位檔案，包含非文本資料（例如圖像、排版訊息等），所以需要使用 `"rb"`，以確保正確處理檔案中的位元組。

其他還可以傳入的文件有：CSV、JSON、HTML、TXT、PPTX、DOCX等。

```python
from openai import OpenAI
client = OpenAI()
file = client.files.create(
    file=open("論文.pdf", "rb"), #代表「讀取二進位檔案」（read binary）
    purpose="assistants"
)
```

創建助理：

```python
assistant = client.beta.assistants.create(
    model="gpt-3.5-turbo",
    name="AI論文回答助手",
    instructions="你是一個學術研究助理，可以透過閱讀使用者上傳的文件，回答人工智慧領域相關論文的問題。",
    tools=[{"type": "retrieval"}], # retrieval是指文件檢索器
    file_ids=[file.id]
)
```

同樣也是要先建立執行緒。

```python
thread = client.beta.threads.create()
```

接著也是要定義一個 `get_response_from_assistant()`，前面已經寫了這邊就不再寫一次。

```python
get_response_from_assistant(assistant, thread, "寫下你想要詢問這篇論文的什麼問題？")
```
"""
)
st.image('./image 2.png', use_column_width=True)

st.markdown(
    """
如果想刪除助手，可以到OpenAI的官方網頁刪除：https://platform.openai.com/assistants

"""
)

st.markdown("## 讀取CSV檔")

def load_data():
    try:
        data = pd.read_csv('personal_data.csv')
        return data
    except FileNotFoundError:
        st.error("找不到檔案")
        return None

data = load_data()
if data is not None:
    st.write("互動表格")
    st.dataframe(data)

st.write("---")

df = pd.DataFrame(data)
st.write("靜態表格")
st.table(df)