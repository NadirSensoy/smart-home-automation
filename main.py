#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main entry point for Smart Home Automation System
"""

import sys
import argparse
import logging
from datetime import datetime

from src.simulation.home_simulator import SmartHomeSimulator, run_simulation_demo
from src.simulation.interactive import run_interactive_simulation
from src.data_simulation.data_generator import generate_sample_dataset
from src.models.model_manager import SmartHomeModelManager
import app

def setup_logging():
    """Set up logging for the application"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_format)
    return logging.getLogger("SmartHomeMain")

def main():
    """Main function to handle command line arguments and run the application"""
    logger = setup_logging()
    
    # Create argument parser
    parser = argparse.ArgumentParser(description="Smart Home Automation System")
    parser.add_argument("--mode", choices=["simulate", "interactive", "train"], default="simulate",
                      help="Operation mode: simulate, interactive, or train")
    parser.add_argument("--steps", type=int, default=100,
                      help="Number of simulation steps")
    parser.add_argument("--step", type=int, dest="steps",
                      help="Alias for --steps")
    parser.add_argument("--no-ml", action="store_true",
                      help="Disable machine learning")
    parser.add_argument("--days", type=int, default=3,
                      help="Number of days to simulate for training")
    
    args = parser.parse_args()
    
    # Run the appropriate mode
    try:
        if args.mode == "simulate":
            logger.info(f"Starting simulation with {args.steps} steps")
            simulator = run_simulation_demo(steps=args.steps, display=True)
            return 0
            
        elif args.mode == "interactive":
            logger.info("Starting interactive simulation")
            run_interactive_simulation()
            return 0
            
        elif args.mode == "train":
            logger.info(f"Training ML model with {args.days} days of data")
            # Generate training data
            dataset = generate_sample_dataset(days=args.days)
            
            # Save to CSV
            import os
            data_dir = os.path.join(os.path.dirname(__file__), "data", "raw")
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
                
            csv_path = os.path.join(data_dir, f"training_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv")
            dataset.to_csv(csv_path, index=False)
            
            # Train model
            model_manager = SmartHomeModelManager()
            model_manager.train_models_for_all_devices(csv_path, model_type='random_forest', optimize=True)
            
            logger.info("Model training completed successfully")
            return 0
        
        else:
            # If we get here, use the existing app entry point
            return app.main()
            
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
