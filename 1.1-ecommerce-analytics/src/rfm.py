import pandas as pd

class RFM:
    def __init__(self, data):
        self.data = data

    def calculate_rfm(self):
        # Calculate Recency, Frequency and Monetary values
        now = pd.Timestamp('now')
        rfm = self.data.groupby('customer_id').agg({
            'order_date': lambda x: (now - x.max()).days,
            'order_id': 'count',
            'total_amount': 'sum'
        })
        rfm.columns = ['recency', 'frequency', 'monetary']
        return rfm

    def segment_customers(self, rfm):
        # Segment customers based on RFM values
        rfm['r_score'] = pd.qcut(rfm['recency'], 5, labels=False)
        rfm['f_score'] = pd.qcut(rfm['frequency'], 5, labels=False)
        rfm['m_score'] = pd.qcut(rfm['monetary'], 5, labels=False)
        rfm['rfm_score'] = rfm['r_score'] + rfm['f_score'] + rfm['m_score']
        return rfm

    def get_segments(self, rfm):
        # Define customer segments
        conditions = [
            (rfm['rfm_score'] >= 9),
            (rfm['rfm_score'] >= 5),
            (rfm['rfm_score'] < 5)
        ]
        choices = ['High Value', 'Medium Value', 'Low Value']
        rfm['segment'] = np.select(conditions, choices, default='No Segment')
        return rfm
