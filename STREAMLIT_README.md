# Movie Night Randomizer - iPhone-Friendly Streamlit App

## Run locally

```bash
pip install -r requirements.txt
streamlit run movie_night_streamlit_app.py
```

Then open the local URL on your computer, or use Streamlit deployment so it works easily on your iPhone.

## Use on iPhone

The best iPhone setup is to deploy this on Streamlit Community Cloud from GitHub:

1. Create a GitHub repo.
2. Add these files:
   - `movie_night_streamlit_app.py`
   - `requirements.txt`
   - your movie Excel file, ideally named `MovieList.xlsx`
3. In Streamlit Community Cloud, deploy the repo.
4. Add this secret in the Streamlit app settings:

```toml
TMDB_API_KEY = "your_tmdb_api_key_here"
```

5. Open the deployed app link in Safari on your iPhone.
6. Use Share → Add to Home Screen to make it feel like an app.

You can also upload the Excel file directly from the sidebar instead of storing it in the repo.
