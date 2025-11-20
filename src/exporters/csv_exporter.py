"""CSV Exporter Module"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class CSVExporter:
    """Export stock analysis data to CSV format"""
    
    def __init__(self, output_dir: str = "data/exports"):
        """
        Initialize CSV exporter
        
        Args:
            output_dir: Directory to save CSV files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export(
        self,
        data: pd.DataFrame,
        filename: Optional[str] = None,
        include_timestamp: bool = True
    ) -> str:
        """
        Export DataFrame to CSV
        
        Args:
            data: DataFrame to export
            filename: Output filename (auto-generated if None)
            include_timestamp: Whether to include timestamp in filename
        
        Returns:
            Path to exported file
        """
        try:
            # Generate filename if not provided
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"stock_analysis_{timestamp}.csv" if include_timestamp else "stock_analysis.csv"
            
            # Ensure .csv extension
            if not filename.endswith('.csv'):
                filename += '.csv'
            
            # Full path
            filepath = self.output_dir / filename
            
            # Export to CSV
            data.to_csv(filepath, index=False)
            
            logger.info(f"Data exported to CSV: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {str(e)}")
            raise
    
    def export_with_metadata(
        self,
        data: pd.DataFrame,
        metadata: dict,
        filename: Optional[str] = None
    ) -> str:
        """
        Export data with metadata header
        
        Args:
            data: DataFrame to export
            metadata: Metadata dictionary
            filename: Output filename
        
        Returns:
            Path to exported file
        """
        try:
            # Generate filename
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"stock_analysis_{timestamp}.csv"
            
            filepath = self.output_dir / filename
            
            # Write metadata as comments
            with open(filepath, 'w') as f:
                f.write("# NSE Stock Analysis Export\n")
                for key, value in metadata.items():
                    f.write(f"# {key}: {value}\n")
                f.write("\n")
            
            # Append data
            data.to_csv(filepath, mode='a', index=False)
            
            logger.info(f"Data with metadata exported to: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error exporting with metadata: {str(e)}")
            raise
