import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s : %(message)s'
)

class CuisineAnalyzer:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.df = None
        self.df_clean = None
        self.all_cuisines = []
        self.cuisine_counts = None
        self.result_df = None
        pass
    def load_data(self):
        try:
            self.df = pd.read_csv(self.csv_file)
            logging.info("Data loaded successfully!" + self.csv_file)
            return self
        except FileNotFoundError:
            logging.error("File not found: " + self.csv_file)
            raise
        except Exception as e:
            logging.error("Error loading file: " + str(e))
            raise

    def validate_data(self):
        required_columns = ['Cuisines']
        missing = [col for col in required_columns if col not in self.df.columns]
        if missing:
            logging.error("Missing required columns: "+ str(missing))
            raise ValueError("Missing columns: " +str(missing))
        logging.info("Data Validation passed!")
        return self
    
    def clean_data(self):
        initial_count = len(self.df)
        self.df_clean = self.df.dropna(subset=['Cuisines'])
        removed_count = initial_count - len(self.df_clean)
        logging.info("Cleaned data: removed " + str(removed_count) +  " rows with missing cuisines")
        logging.info("Working with " + str(len(self.df_clean))+ "restaurants") 
        return self
    
    def parse_cuisines(self):
        self.all_cuisines = []
        for cuisines_string in self.df_clean['Cuisines']:
            if not isinstance(cuisines_string, str):
                continue
            cuisines = [cuisine.strip() for cuisine in cuisines_string.split(',')]
            self.all_cuisines.extend(cuisines)
        logging.info("Parsed " + str(len(self.all_cuisines)) + " individual cuisine entries")
        logging.info("Found " + str(len(set(self.all_cuisines))) + " unique cuisines")
        return self
    
    def count_cuisines(self):
        self.cuisine_counts = Counter(self.all_cuisines)
        logging.info("Cuisine counting complete")
        return self
    
    def analyze_top_cuisine(self, top_n=3):
        if self.cuisine_counts is None:
            raise RuntimeError("Must call count_cuisines() first")
        top_cuisines = self.cuisine_counts.most_common(top_n)
        total_restaurants = len(self.df_clean)
        results = []
        for rank , (cuisine, count) in enumerate(top_cuisines, 1):
            percentage = (count / total_restaurants) * 100

            results.append({
                'Rank': rank,
                'Cuisine': cuisine,
                'Count': count,
                'Total Restaurants': total_restaurants,
                'Percentage' : round(percentage, 2)
            })

        self.result_df = pd.DataFrame(results)
        logging.info("Analysis complete for top " + str(top_n) + " cuisines")
        return self
    
    def display_results(self):
        print(" TOP 3 CUISINES ANALYSIS")
        print("\n" + str(self.result_df.to_string(index=False)))
        print("\n Summary ")
        for idx, row in self.result_df.iterrows():
            print("\n#{rank}: {cuisine}". format(rank=row['Rank'], cuisine=row['Cuisine']))
            print("  Count: {count} restaurants".format(count=row['Count']))
            print("  Percentage: {pct}% (out of {total} restaurants)".format( pct=row['Percentage'], total=row['Total Restaurants']))
        return self
        
    def save_results(self, output_file= 'cuisine_analysis_result.csv'):
        self.result_df.to_csv(output_file, index=False)
        logging.info("Results saved to: " + output_file)
        return self
    
    def create_visualization(self, output_image= 'cuisine_analysis_charts.png'):
        cuisines = self.result_df['Cuisine'].tolist()
        counts = self.result_df['Count'].tolist()
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14,6))
        colors = ["#0977ED", "#EC7C0D", "#3CD428"]
        
        #bar graph

        bars = ax1.bar(cuisines, counts, color=colors[:len(cuisines)],edgecolor='black', linewidth=1.5, alpha=0.8)
        ax1.set_xlabel('Cuisine', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Number of restaurants', fontsize=12, fontweight='bold')
        ax1.set_title('Top 3 Most Popular Restaurant Cuisines' , fontsize=16, fontweight='bold', pad=15)
        ax1.grid(axis='y',linestyle='--',linewidth=0.7, alpha=0.5 )

        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height, '{}'.format(int(count)), ha='center', va='bottom', fontweight='bold', fontsize=11)
        
        #pie chart
        
        percentages = self.result_df['Percentage'].tolist()
        wedges, texts, autotexts = ax2.pie( percentages, labels=cuisines, autopct='%1.1f%%', colors=colors[:len(cuisines)], startangle=90,wedgeprops={'edgecolor':'white', 'linewidth':2}, textprops={'fontsize':11, 'fontweight':'bold'})
        ax2.set_title('Percentage Distribution of Top 3 Cuisines', fontsize=16, fontweight='bold', pad=15)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(10)

        plt.tight_layout()
        plt.savefig(output_image, dpi=300, bbox_inches='tight')
        logging.info("Visualizations saved to: "+output_image)
        plt.show()

        return self
    
    def run_complete_analysis(self):
        (self.load_data()
         .validate_data()
         .clean_data()
         .parse_cuisines()
         .count_cuisines()
         .analyze_top_cuisine()
         .display_results()
         .save_results('cuisine_analysis_results.csv')
         .create_visualization('cuisine_analysis_charts.png'))
        
        print("\n Analysis Complete!")
        print(" File created:")
        print("  -cuisine_analysis_results.csv")
        print("  -cuisine_analysis_charts.png")
    
if __name__ == "__main__":
    try:
        analyzer = CuisineAnalyzer('cleaned_restaurants.csv')
        analyzer.run_complete_analysis()

    except FileNotFoundError:
        print("\nError: 'cleaned_restaurants.csv not found!")
    except Exception as e:
        print("\nError during Analysis: " + str(e))
        logging.error("Analysis failed: " + str(e))
