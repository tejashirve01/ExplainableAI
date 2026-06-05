Installation

Clone the repository:

git clone https://github.com/tejashirve01/ExplainableAI

cd ExplainableAI

Create a virtual environment:

python -m venv venv

Activate it:

Windows:

venv\Scripts\activate

Install dependencies:

cd backend
pip install -r requirements.txt

Create a .env file in backend folder with

GEMINI_API_KEY=your_api_key

Create a .env file in frontend folder with

REACT_APP_API_URL=your_app_url take from another terminal where backend will be hosted.

Running the Project

cd backend
uvicorn api:app --reload

In another terminal

cd frontend

Note: put your_app_url in .env

npm install
npm start

You're set to go.


Technologies Used

Python

Sentence Transformers

FAISS

HuggingFace Transformers

Scikit-learn

PyMuPDF

Author

Tejas Hirve
