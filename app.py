from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# Load the CSV file into a pandas DataFrame
anime_data = pd.read_csv("C:\\Users\\abhi2\\Downloads\\Anime.csv")

# Clean the data: Remove rows with missing values and unnecessary columns
anime_data.dropna(subset=['Tags', 'Rating'], inplace=True)

# Process the data: Split and expand the 'Tags' column
anime_data['Tags'] = anime_data['Tags'].str.split(', ')


# Calculate similarity between anime based on their tags
def calculate_similarity(anime1_tags, anime2_tags):
    common_tags = set(anime1_tags) & set(anime2_tags)
    total_tags = set(anime1_tags) | set(anime2_tags)
    similarity = len(common_tags) / len(total_tags)
    return similarity


# Recommend similar anime based on the input anime's name
def recommend_similar_anime(input_anime):
    input_tags = anime_data.loc[anime_data['Name'] == input_anime, 'Tags'].iloc[0]
    anime_data['Similarity'] = anime_data['Tags'].apply(lambda x: calculate_similarity(input_tags, x))
    similar_anime = anime_data[~anime_data['Name'].str.contains(input_anime, case=False)].sort_values(by='Similarity',
                                                                                                      ascending=False)

    return similar_anime[['Name', 'Rating']].head(10)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    keyword = request.form['keyword']
    search_results = anime_data[anime_data['Name'].str.contains(keyword, case=False)].copy()
    search_results['Name_length'] = search_results['Name'].str.len()
    search_results.sort_values(by='Name_length', inplace=True)
    search_results.drop('Name_length', axis=1, inplace=True)
    return render_template('search.html', keyword=keyword, search_results=search_results)


@app.route('/recommend', methods=['GET'])
def recommend():
    input_anime = request.args.get('input_anime')
    similar_anime_recommendation = recommend_similar_anime(input_anime)
    return render_template('recommend.html', input_anime=input_anime,
                           similar_anime_recommendation=similar_anime_recommendation)


if __name__ == '__main__':
    app.run(debug=False,host='0.0.0.0')
