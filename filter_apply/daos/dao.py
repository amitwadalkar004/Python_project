from src.filter_apply.models.model import DataModel
from src.db_session import SessionLocal
from sqlalchemy import update, func, Integer, cast

from src.utils.logs import CustomLogger


logger_instance = CustomLogger(log_level='DEBUG', log_file_name='filterapply.log', log_path='logs')
logger = logger_instance.get_logger()

class dao:
    def __init__(self):
        self.session = SessionLocal()
        
    # def save_filtered_data(self, filtered_data, file_name):
    #     try:
    #         # Save the filtered data
    #         filtered_data.to_csv(f'{file_name}_filtered.csv', index=False)
    #         return "filtered_data successfully saved."
    #     except Exception as e:
    #         logger.error(f"Error in save_filtered_data: {e}")
    #         raise e