import argparse
from agent import WebAgent
import time
import sys

def train_mode(agent, url):
    """Training mode for demonstrating ad rating"""
    try:
        print("Starting training mode...")
        print("Navigate to ads and interact with them. Rate each ad sequence when done.")
        print("Commands: rate [0-1], next, done")
        
        agent.start_training_sequence()
        agent.navigate_to(url)
        
        while True:
            command = input("\nEnter command (rate [0-1], next, done): ").strip().lower()
            
            if command == 'done':
                break
            elif command == 'next':
                # Save current sequence if any and start new one
                print("Starting new sequence...")
                agent.end_training_sequence(0)  # Default to negative rating
                agent.start_training_sequence()
                continue
            elif command.startswith('rate '):
                try:
                    rating = float(command.split()[1])
                    if 0 <= rating <= 1:
                        print(f"Rating current sequence: {rating}")
                        agent.end_training_sequence(rating)
                        agent.start_training_sequence()
                    else:
                        print("Rating must be between 0 and 1")
                except (IndexError, ValueError):
                    print("Invalid rating format. Use: rate [0-1]")
            else:
                print("Unknown command")
        
        # Train model with collected data
        print("\nTraining model with collected sequences...")
        history = agent.train_model()
        if history:
            print("Model trained successfully!")
            
        # Save training data
        agent.save_training_data()
        print("Training data saved!")
        
    except Exception as e:
        print(f"Error in training mode: {str(e)}")

def predict_mode(agent, url):
    """Prediction mode for rating ads"""
    try:
        print("Starting prediction mode...")
        agent.start_recording()
        agent.navigate_to(url)
        
        # Detect ads
        ad_data = agent.detect_ad_content()
        if ad_data and ad_data['count'] > 0:
            print(f"\nFound {ad_data['count']} ads on the page")
            print("Types:", ', '.join(ad_data['types']))
            
            # Get prediction for current sequence
            prediction = agent.predict_rating()
            if prediction is not None:
                print(f"\nPredicted rating: {prediction:.2f}")
        else:
            print("No ads detected on the page")
        
    except Exception as e:
        print(f"Error in prediction mode: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Web Agent CLI with Ad Rating')
    parser.add_argument('--url', type=str, required=True, help='URL to navigate to')
    parser.add_argument('--mode', choices=['train', 'predict'], required=True, 
                      help='Operation mode: train (for learning) or predict (for rating)')
    parser.add_argument('--scroll', choices=['up', 'down'], help='Scroll direction')
    parser.add_argument('--scroll-amount', type=int, default=300, help='Scroll amount in pixels')
    parser.add_argument('--click', type=str, help='Click coordinates (format: x,y)')
    
    args = parser.parse_args()
    
    agent = WebAgent()
    
    try:
        print("Initializing web agent...")
        agent.initialize()
        
        if args.mode == 'train':
            train_mode(agent, args.url)
        else:  # predict mode
            predict_mode(agent, args.url)
            
        if args.scroll:
            print(f"Scrolling {args.scroll}...")
            agent.scroll(args.scroll, args.scroll_amount)
            time.sleep(1)
        
        if args.click:
            try:
                x, y = map(int, args.click.split(','))
                print(f"Clicking at coordinates ({x}, {y})...")
                agent.click(x, y)
                time.sleep(1)
            except ValueError:
                print("Error: Click coordinates must be in format 'x,y'")
        
        input("Press Enter to close the browser...")
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        agent.close()

if __name__ == "__main__":
    main()
