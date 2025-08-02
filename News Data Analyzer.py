from bs4 import BeautifulSoup
import requests
import matplotlib.pyplot as plt
from collections import Counter
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import folium

def main():
    print("\n" + "="*50)
    print("NEWS DATA ANALYZER - MAIN MENU".center(50))
    print("="*50)
    urls = [
    "https://tribune.com.pk/",
    "https://www.dawn.com/", 
    "https://www.nation.com.pk/"
    ]
    for url in urls:
        headlines = scrape_news_headlines(url)
        print(f"\nHeadlines from {url}:")
        for i, headline in enumerate(headlines[:], 1):  
            print(f"{i}. {headline}")
            
    while True:
        print("\n" + "-"*50)
       
        print("Analysis options:")
        print("1. Word Frequency Analysis")
        print("2. Geographical Heatmap Generator")
        print("3. Sentiment Analysis")
        print("4. Exit")
        
        choice = input("Select analysis (1-5): ").strip()
        
        if choice == "1":
            word_frequency_analysis(headlines)
        elif choice == "2":
            geographical_heatmap(headlines)
        elif choice == "3":
            sentiment_analysis(headlines)
        elif choice == "4":
            print("Exiting program...")
            break
        else:
            print("Invalid choice. Try again.")

def scrape_news_headlines(url):
    response = requests.get(url)
    print(f"Status code for {url}: {response.status_code}")
    soup = BeautifulSoup(response.text, 'html.parser')
    topstories = []
    
    # Words/phrases to exclude from ALL news sources
    excluded_terms = {
        'sports', 'business', 'fashion', 'national', 'world',
        'entertainment', 'technology', 'health', 'videos',
        'latest news', 'today\'s paper', 'e-paper', 'magazines',
        'home', 'latest', 'instep', 'makes', 'housing',
        'follow us', 'contact us', 'subscription', 'email us', 'epaper nawaiwaqt',
        'newsletter subscription'
    }
    
    # Scrape headlines from standard title tags
    for h in soup.select('h1[class*="title"], h2[class*="title"], h3[class*="title"], h4[class*="title"]'):
        headline = h.get_text().strip()
        cleaned = ' '.join(headline.split())
        
        # Apply filters to ALL sources
        is_valid_length = 15 <= len(cleaned) <= 150
        is_not_section = cleaned.lower() not in excluded_terms
        
        if is_valid_length and is_not_section:
            topstories.append(cleaned)
    
    return topstories


        
def  word_frequency_analysis(headlines):
    words = []
    for headline in headlines:
        words.extend([word.lower()
                     for word in headline.split() 
                        if len(word) > 3 ])
    stop_word= {'this', 'that', 'with', 'will','where','what','wait', 'from', 'have', 'more', 'when','reveals', 'very', "pakistan's", 'after', 'before', 'first', 'second', 'says', 'said', 'tells', 'ties', 'amid'}
    filtered_word = [word for word in words if word not in stop_word]

    word_counts = Counter(filtered_word).most_common(5) # collections method to get the most common words is useful 
    word, counts = zip(*word_counts)
    plt.barh(word, counts, color = 'navy')
    plt.xlabel('COUNT')
    plt.ylabel('WORD')
    plt.title('Most occuring words in Pakistani News Paper')
    plt.show()
    return word_counts


def geographical_heatmap(headlines):

    key_words = [
        'raid', 'raids', 'bombing', 'bombs', 'blast', 'blasts', 'terror', 
        'attack', 'attacks', 'strike', 'airstrike', 'shooting', 'shootout',
        'earthquake', 'flood', 'floods', 'cyclone', 'typhoon', 'hurricane', 
        'landslide', 'avalanche', 'wildfire', 'tsunami', 'drought',
       'tragedy', 'disaster', 'disasters', 'crisis', 'famine', 'plague',
        'protest', 'protests', 'riot', 'riots', 'demonstration', 'uprising',
       'collision', 'derailment', 'sinking', 'crash', 'explosion'
    ]
    
    crisis_headlines = [
        headline for headline in headlines
        if any(keyword in headline.lower() for keyword in key_words)
    ]
    
    print(f"\nFound {len(crisis_headlines)} crisis-related headlines:")
    for i, headline in enumerate(crisis_headlines[:10], 1): 
        print(f"{i}. {headline}") 
       
    major_cities = [
       # Major Cities
    "karachi", "lahore", "faisalabad", "rawalpindi",
    "gujranwala", "peshawar", "multan", "hyderabad", 
    "islamabad", "muridke", "sialkot", "bahawalpur",
    
    # Regions/Districts
    "bajaur", "north waziristan", "south waziristan", 
    "gilgit", "baltistan", "hunza", "skardu", "diamer",
    "chitral", "swat", "malakand", "mardan", "kohat",
    "dera ismail khan", "bannu", "tank", "lakki marwat",
    
    # Provinces/Territories
    "punjab", "sindh", "balochistan", "khyber pakhtunkhwa",
    "kpk", "gilgit baltistan", "ajk", "azad kashmir",
    "fata", "tribal areas",
    
    # Common Abbreviations
    "isb", "khi", "lhr", "quetta city", "peshawar city",
    "gb", "ict", "kp", "nwfp",
    
    # Neighboring Countries/Regions
    "afghanistan", "kabul", "kandahar",
    "india", "new delhi", "kashmir", "srinagar",
    "china", "xinjiang", "iran", "us", "uk"
    "tajikistan","pahalgam"
    
    # Important Landmarks
    "k2", "nanga parbat", "indus river", 
    "sutlej", "chenab", "jhelum", "swat valley",
    "khunjerab pass", "gwadar port"
] 
    
    place_headlines = [
        cheadline for cheadline in crisis_headlines
        if any(keyword in cheadline.lower() for keyword in major_cities)
    ]  
    print(f"\nFound {len(place_headlines)} place-related headlines:")
    for i, headline in enumerate(place_headlines[:10], 1): 
        print(f"{i}. {headline}")
    
    """New mapping integration (added at the end)"""
    # 1. Initialize geocoder
    geolocator = Nominatim(user_agent="news_analyzer")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    
    # 2. Prepare map centered on Pakistan
    pak_map = folium.Map(location=[30.3753, 69.3451], zoom_start=6)
    
    # 3. Process each location-containing headline
    for headline in place_headlines:
        # Find which city is mentioned
        city = next((city for city in major_cities 
                    if city in headline.lower()), None)
        
        if city:
            try:
                location = geocode(f"{city}, Pakistan") # pakistan only map
                if location:
                    # Add marker to map
                    folium.Marker(
                        location=[location.latitude, location.longitude],
                        popup=f"<b>{city.title()}</b><br>{headline}",
                        icon=folium.Icon(color='red')
                    ).add_to(pak_map)
            except Exception as e:
                print(f"Couldn't geocode {city}: {e}")
    
    # 4. Save and return the map
    pak_map.save("pakistan_crisis_map.html")
    print("\nMap generated as 'pakistan_crisis_map.html'")
    return pak_map

def sentiment_analysis(headlines):
   #scoring criteria 
   positive_news = 0
   negative_news = 0
   neutral_news = 0 
   for headline in headlines:
       score = analyze_score(headline)
       if score > 0:
           positive_news += 1
       elif score < 0:
           negative_news += 1
       else:
           neutral_news += 1

   counts = [negative_news, neutral_news, positive_news]
   labels = ["Negative", "Neutral", "Positive"]
   colors = ["red", "blue", "green"]
   plt.figure(figsize=(8, 5))
   plt.pie(counts, labels=labels, colors=colors, autopct='%1.1f%%')
   plt.title("Sentiment Distribution (%)")
   plt.show()
   return


def analyze_score(headline):
    positive_words = [
    'peace', 'recovery', 'rebuild', 'progress', 'reform', 'advance', 'breakthrough',
    'cooperation', 'unity', 'accord', 'deal', 'agreement', 'truce', 'ceasefire', 'dialogue',
    'win', 'achievement', 'success', 'triumph', 'milestone', 'record',
    'aid', 'relief', 'donation', 'support', 'rescue', 'volunteer', 'charity',
    'hope', 'optimism', 'revival', 'renewal', 'stability',
    'evacuation', 'shelter', 'rehabilitation', 'reconstruction',
    'cure', 'vaccine', 'treatment', 'improve',
    'growth', 'surplus', 'boom', 'investment', 'stabilize',
    'justice', 'arrest', 'verdict', 'compensation', 'rights',

    'resilient', 'strong', 'brave', 'heroic',
    'historic', 'unprecedented', 'landmark'
    ]
   
    negative_words = [
    'raid', 'raids', 'bombing', 'bombs', 'blast', 'blasts', 'terror', 
    'attack', 'attacks', 'strike', 'airstrike', 'shooting', 'shootout',
    'war', 'conflict', 'clash', 'violence', 'murder', 'assassination',
    'earthquake', 'flood', 'floods', 'cyclone', 'typhoon', 'hurricane', 
    'landslide', 'avalanche', 'wildfire', 'tsunami', 'drought',
    'tragedy', 'disaster', 'disasters', 'crisis', 'famine', 'plague', 'pandemic',
    'death', 'fatal', 'casualty', 'injury', 'missing',
    'protest', 'protests', 'riot', 'riots', 'demonstration', 'uprising', 'rebellion',
    'strike', 'blockade', 'curfew', 'crackdown',
    'corruption', 'scam', 'fraud', 'scandal',
    'inflation', 'recession', 'poverty', 'unemployment',
    'failure', 'collapse', 'bankruptcy', 'default',
    'deadly', 'fatal', 'horrific', 'brutal', 'chaos', 'havoc'
    ]
    positive = sum(word in headline.lower() for word in positive_words)
    negative = sum(word in headline.lower() for word in negative_words)

    return positive - negative


        

if __name__ == "__main__":
    main()


