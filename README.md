CTcue Analyzer
=========

## Development

Required:
- Python 2.7
- Natural Language ToolKit (NLTK)
- Flask
- Tornado

To start backend run
- python /api.py

The server runs on `http://127.0.0.1:5000` by default

Example on server (inside the directory):

`python api.py --host 188.226.214.70 --port 5000`

## Install

Assuming you have pip.

* sudo pip install nltk
* sudo python -m nltk.downloader -d /usr/share/nltk_data all
* sudo pip install flask
* sudo pip install -U flask-cors
* sudo pip install whoosh
* sudo pip install tornado

## Extraction

Supported tasks:
- Tokenize
- Split sentences
- Extract health scores

All tasks require data to be submitted using POST requests with content-type application/json.

### Tokenize
```python
data    = {"text" : "Example sentences, which can be tokenized. We can also split the sentences."}
headers = {'Content-Type': 'application/json'}
url     = "http://127.0.0.1:5000/api/simple/tokenize"

requests.post(url, data=json.dumps(data), headers=headers)
```

Result:
A list of words.
```python
{
  "result" : ["Example", "sentences", ",", "which", "can", "be", "tokenized", ".", "We", "can", "also", "split", "the", "sentences", "."]
}
```


### Split sentences
```python
data    = {"text" : "Example sentences, which can be tokenized. We can also split the sentences."}
headers = {'Content-Type': 'application/json'}
url     = "http://127.0.0.1:5000/api/simple/sentence_split"

requests.post(url, data=json.dumps(data), headers=headers)
```

Result:
A list of sentences.
```python
{
  "result": [
    "Example sentences, which can be tokenized.",
    "We can also split the sentences."
  ]
}
```

### Extract health scores
```python
data =
{
    "text": "Example sentences, which can be tokenized. We can also split the sentences. We can extract scores like an agatston score of 432.",
    "health_scores": {
        "agatston": {
            "synonyms": [
                "agatston",
                "agatston-score",
                "agatstonscore",
                "kalkscore",
                "calciumscore"
            ],
            "values": {
                "type": "int",
                "min": 0,
                "max": 9999,
                "format": "(\\-*\\d+)((,|\\.)\\d+)?",
                "group": 0
            }
        }
    }
}

headers = {'Content-Type': 'application/json'}
url     = "http://127.0.0.1:5000/api/extract/health_scores"

requests.post(url, data=json.dumps(data), headers=headers)
```

The variable health_scores is a json object that contains the scores that need to be extracted. These scores are identified by a name and contain a list of synonyms and a set of constraints that the scores should match. These constraints include the value type (int, float), the minimum and maximum value the score can have, and a string indicating the format (as regex). Finally, group indicates the regex group that contains the actual value. The json object can contain an unlimited number of health scores. The value constraints are optional, without it the system makes a "best guess." For synonyms it is advised to also add the original name of the score to the list.


Result:
The resulting json objects contains for each requested health score a list of identified scores with evidence of why this value was extracted.
```python
{
    "result": {
        "agatston": [
            {
                "sentenceNr": 2,
                "start": 30,
                "term": "agatston",
                "values": [
                    432
                ]
            }
        ],
        "sentences": [
            "Example sentences, which can be tokenized.",
            "We can also split the sentences.",
            "We can extract scores like an <em class=\"highlight\">agatston</em> score of 432."
        ]
    },
    "status": 200
}
```
