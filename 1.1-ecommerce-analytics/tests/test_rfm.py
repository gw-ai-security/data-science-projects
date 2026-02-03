"""
Comprehensive tests for RFM segmentation module.

Tests cover:
- Data loading and validation
- RFM metric computation
- Quantile-based scoring
- Segment assignment rules
- Edge cases (empty data, single customer, duplicates)
"""

from pathlib import Path
import pandas as pd
import pytest
import tempfile
import numpy as np

from src.rfm import (
    load_transactions,
    compute_rfm,
    score_rfm,
    assign_segments,
    save_segment_summary,
)


@pytest.fixture
def sample_transactions():
    """Create sample transaction data for testing."""
    df = pd.DataFrame({
        "InvoiceNo": ["INV001", "INV002", "INV003", "INV004", "INV005"],
        "InvoiceDate": pd.to_datetime([
            "2011-12-01", "2011-12-02", "2011-12-03", "2011-12-04", "2011-12-05"
        ]),
        "CustomerID": [1001, 1001, 1002, 1002, 1003],
        "Quantity": [2, 3, 1, 5, 2],
        "UnitPrice": [10.0, 15.0, 20.0, 25.0, 30.0],
    })
    df["Revenue"] = df["Quantity"] * df["UnitPrice"]
    return df


@pytest.fixture
def sample_rfm():
    """Create sample RFM data for testing."""
    return pd.DataFrame({
        "CustomerID": [1001, 1002, 1003, 1004, 1005],
        "Recency": [5, 50, 100, 200, 300],
        "Frequency": [10, 8, 5, 3, 1],
        "Monetary": [5000, 3000, 1500, 800, 200],
    })


class TestLoadTransactions:
    """Tests for load_transactions function."""
    
    def test_load_valid_data(self, sample_transactions, tmp_path):
        """Test loading valid transaction data."""
        # Save sample data
        path = tmp_path / "test_data.parquet"
        sample_transactions.to_parquet(path)
        
        # Load it
        df = load_transactions(path)
        
        # Check basics
        assert len(df) == 5
        assert "Revenue" in df.columns
        assert df["Revenue"].iloc[0] == 20.0  # 2 * 10.0
    
    def test_load_missing_required_column(self, tmp_path):
        """Test that missing required columns raise an error."""
        # Create data without CustomerID
        df = pd.DataFrame({
            "InvoiceNo": ["INV001"],
            "InvoiceDate": ["2011-12-01"],
            "Quantity": [2],
            "UnitPrice": [10.0],
        })
        path = tmp_path / "bad_data.parquet"
        df.to_parquet(path)
        
        # Should raise assertion error
        with pytest.raises(AssertionError, match="Missing required columns"):
            load_transactions(path)
    
    def test_load_drops_missing_customer_id(self, tmp_path):
        """Test that rows with missing CustomerID are dropped."""
        df = pd.DataFrame({
            "InvoiceNo": ["INV001", "INV002"],
            "InvoiceDate": ["2011-12-01", "2011-12-02"],
            "CustomerID": [1001.0, None],
            "Quantity": [2, 3],
            "UnitPrice": [10.0, 15.0],
        })
        path = tmp_path / "missing_customer.parquet"
        df.to_parquet(path)
        
        result = load_transactions(path)
        assert len(result) == 1  # Only one row with valid CustomerID


class TestComputeRFM:
    """Tests for compute_rfm function."""
    
    def test_compute_basic_rfm(self, sample_transactions):
        """Test basic RFM computation."""
        snapshot = pd.Timestamp("2011-12-10")
        rfm = compute_rfm(sample_transactions, snapshot_date=snapshot)
        
        # Check structure
        assert len(rfm) == 3  # Three unique customers
        assert list(rfm.columns) == ["CustomerID", "Recency", "Frequency", "Monetary"]
        
        # Check customer 1001 (two purchases on Dec 1 and 2, last on Dec 2)
        cust_1001 = rfm[rfm["CustomerID"] == 1001].iloc[0]
        assert cust_1001["Recency"] == 8  # Dec 10 - Dec 2 = 8 days
        assert cust_1001["Frequency"] == 2  # Two unique invoices
        assert cust_1001["Monetary"] == 65.0  # (2*10) + (3*15) = 65
    
    def test_compute_rfm_single_customer(self):
        """Test RFM computation with single customer."""
        df = pd.DataFrame({
            "InvoiceNo": ["INV001"],
            "InvoiceDate": pd.to_datetime(["2011-12-01"]),
            "CustomerID": [1001],
            "Quantity": [2],
            "UnitPrice": [10.0],
            "Revenue": [20.0],
        })
        
        snapshot = pd.Timestamp("2011-12-10")
        rfm = compute_rfm(df, snapshot_date=snapshot)
        
        assert len(rfm) == 1
        assert rfm["Recency"].iloc[0] == 9
        assert rfm["Frequency"].iloc[0] == 1
        assert rfm["Monetary"].iloc[0] == 20.0
    
    def test_compute_rfm_default_snapshot(self, sample_transactions):
        """Test that default snapshot date is max date + 1."""
        rfm = compute_rfm(sample_transactions)
        
        # Snapshot should be 2011-12-06 (max date 2011-12-05 + 1 day)
        # Customer 1003 last purchase on 2011-12-05
        cust_1003 = rfm[rfm["CustomerID"] == 1003].iloc[0]
        assert cust_1003["Recency"] == 1  # 1 day ago
    
    def test_compute_rfm_assertions(self):
        """Test that invalid data triggers assertions."""
        # Create data that would produce negative recency
        df = pd.DataFrame({
            "InvoiceNo": ["INV001"],
            "InvoiceDate": pd.to_datetime(["2011-12-10"]),
            "CustomerID": [1001],
            "Quantity": [2],
            "UnitPrice": [10.0],
            "Revenue": [20.0],
        })
        
        snapshot = pd.Timestamp("2011-12-05")  # Before the transaction
        
        with pytest.raises(AssertionError, match="negative Recency"):
            compute_rfm(df, snapshot_date=snapshot)


class TestScoreRFM:
    """Tests for score_rfm function."""
    
    def test_score_basic(self, sample_rfm):
        """Test basic RFM scoring."""
        scored = score_rfm(sample_rfm, bins=5)
        
        # Check columns exist
        assert "R_Score" in scored.columns
        assert "F_Score" in scored.columns
        assert "M_Score" in scored.columns
        assert "RFM_Score" in scored.columns
        
        # Check scores are in valid range
        assert scored["R_Score"].between(1, 5).all()
        assert scored["F_Score"].between(1, 5).all()
        assert scored["M_Score"].between(1, 5).all()
    
    def test_score_recency_inverted(self, sample_rfm):
        """Test that recency scoring is inverted (lower = better)."""
        scored = score_rfm(sample_rfm, bins=5)
        
        # Customer with Recency=5 (most recent) should have high R_Score
        best_recency = scored[scored["Recency"] == 5].iloc[0]
        worst_recency = scored[scored["Recency"] == 300].iloc[0]
        
        assert best_recency["R_Score"] > worst_recency["R_Score"]
    
    def test_score_frequency_normal(self, sample_rfm):
        """Test that frequency scoring is normal (higher = better)."""
        scored = score_rfm(sample_rfm, bins=5)
        
        # Customer with Frequency=10 should have high F_Score
        best_freq = scored[scored["Frequency"] == 10].iloc[0]
        worst_freq = scored[scored["Frequency"] == 1].iloc[0]
        
        assert best_freq["F_Score"] > worst_freq["F_Score"]
    
    def test_score_monetary_normal(self, sample_rfm):
        """Test that monetary scoring is normal (higher = better)."""
        scored = score_rfm(sample_rfm, bins=5)
        
        # Customer with Monetary=5000 should have high M_Score
        best_mon = scored[scored["Monetary"] == 5000].iloc[0]
        worst_mon = scored[scored["Monetary"] == 200].iloc[0]
        
        assert best_mon["M_Score"] > worst_mon["M_Score"]
    
    def test_score_handles_duplicates(self):
        """Test that scoring handles duplicate values gracefully."""
        # Create data with many duplicate values
        rfm = pd.DataFrame({
            "CustomerID": range(20),
            "Recency": [10] * 10 + [50] * 10,  # Only 2 unique values
            "Frequency": [5] * 10 + [10] * 10,
            "Monetary": [100] * 10 + [200] * 10,
        })
        
        # Should not raise error
        scored = score_rfm(rfm, bins=5)
        
        # Scores should still be integers
        assert scored["R_Score"].dtype == int
        assert scored["F_Score"].dtype == int
        assert scored["M_Score"].dtype == int
    
    def test_score_rfm_string(self, sample_rfm):
        """Test that RFM_Score is a string concatenation."""
        scored = score_rfm(sample_rfm, bins=5)
        
        # RFM_Score should be R + F + M as string
        first = scored.iloc[0]
        expected = f"{first['R_Score']}{first['F_Score']}{first['M_Score']}"
        assert first["RFM_Score"] == expected


class TestAssignSegments:
    """Tests for assign_segments function."""
    
    def test_assign_vip_segment(self):
        """Test VIP segment assignment."""
        rfm_scored = pd.DataFrame({
            "CustomerID": [1001],
            "Recency": [5],
            "Frequency": [20],
            "Monetary": [10000],
            "R_Score": [5],
            "F_Score": [5],
            "M_Score": [5],
            "RFM_Score": ["555"],
        })
        
        result = assign_segments(rfm_scored)
        assert result["Segment"].iloc[0] == "VIP"
    
    def test_assign_loyal_segment(self):
        """Test Loyal segment assignment."""
        rfm_scored = pd.DataFrame({
            "CustomerID": [1001],
            "Recency": [30],
            "Frequency": [15],
            "Monetary": [5000],
            "R_Score": [3],
            "F_Score": [5],
            "M_Score": [4],
            "RFM_Score": ["354"],
        })
        
        result = assign_segments(rfm_scored)
        assert result["Segment"].iloc[0] == "Loyal"
    
    def test_assign_growth_potential_segment(self):
        """Test Growth Potential segment assignment."""
        rfm_scored = pd.DataFrame({
            "CustomerID": [1001],
            "Recency": [5],
            "Frequency": [1],
            "Monetary": [100],
            "R_Score": [5],
            "F_Score": [1],
            "M_Score": [1],
            "RFM_Score": ["511"],
        })
        
        result = assign_segments(rfm_scored)
        assert result["Segment"].iloc[0] == "Growth Potential"
    
    
    def test_assign_at_risk_segment_corrected(self):
        """Test At Risk segment assignment with correct criteria."""
        rfm_scored = pd.DataFrame({
            "CustomerID": [1001],
            "Recency": [150],
            "Frequency": [8],
            "Monetary": [3000],
            "R_Score": [1],  # Must be <= 2 for At Risk
            "F_Score": [4],  # Must be >= 3
            "M_Score": [3],  # Must be >= 2
            "RFM_Score": ["143"],
        })
        
        result = assign_segments(rfm_scored)
        assert result["Segment"].iloc[0] == "At Risk"
    
    def test_assign_dormant_segment(self):
        """Test Dormant segment assignment."""
        rfm_scored = pd.DataFrame({
            "CustomerID": [1001],
            "Recency": [300],
            "Frequency": [2],
            "Monetary": [500],
            "R_Score": [1],
            "F_Score": [2],
            "M_Score": [2],
            "RFM_Score": ["122"],
        })
        
        result = assign_segments(rfm_scored)
        assert result["Segment"].iloc[0] == "Dormant"
    
    def test_assign_mainstream_segment(self):
        """Test Mainstream segment (default)."""
        rfm_scored = pd.DataFrame({
            "CustomerID": [1001],
            "Recency": [50],
            "Frequency": [3],
            "Monetary": [1000],
            "R_Score": [3],
            "F_Score": [3],
            "M_Score": [3],
            "RFM_Score": ["333"],
        })
        
        result = assign_segments(rfm_scored)
        assert result["Segment"].iloc[0] == "Mainstream"
    
    def test_all_segments_covered(self):
        """Test that various score combinations produce valid segments."""
        # Create diverse score combinations
        rfm_scored = pd.DataFrame({
            "CustomerID": range(10),
            "Recency": [5, 50, 100, 200, 300, 10, 150, 80, 120, 250],
            "Frequency": [20, 15, 10, 8, 2, 1, 5, 3, 4, 6],
            "Monetary": [10000, 5000, 3000, 2000, 500, 100, 1500, 800, 1200, 1800],
            "R_Score": [5, 4, 3, 2, 1, 5, 2, 3, 2, 1],
            "F_Score": [5, 5, 4, 4, 1, 1, 3, 2, 3, 3],
            "M_Score": [5, 4, 3, 3, 1, 1, 2, 2, 2, 3],
            "RFM_Score": ["555", "454", "343", "243", "111", "511", "232", "322", "232", "133"],
        })
        
        result = assign_segments(rfm_scored)
        
        # All segments should be valid
        valid_segments = {"VIP", "Loyal", "Growth Potential", "At Risk", "Dormant", "Mainstream"}
        assert result["Segment"].isin(valid_segments).all()


class TestSaveSegmentSummary:
    """Tests for save_segment_summary function."""
    
    def test_save_creates_files(self, tmp_path):
        """Test that save creates markdown and CSV files."""
        rfm_segmented = pd.DataFrame({
            "CustomerID": [1001, 1002, 1003],
            "Recency": [5, 50, 300],
            "Frequency": [10, 5, 1],
            "Monetary": [5000, 1500, 200],
            "R_Score": [5, 3, 1],
            "F_Score": [5, 3, 1],
            "M_Score": [5, 3, 1],
            "RFM_Score": ["555", "333", "111"],
            "Segment": ["VIP", "Mainstream", "Dormant"],
        })
        
        md_path = tmp_path / "summary.md"
        save_segment_summary(rfm_segmented, md_path)
        
        # Check markdown file exists
        assert md_path.exists()
        content = md_path.read_text()
        assert "# RFM Segmentation Summary" in content
        assert "VIP" in content
        assert "Mainstream" in content
        
        # Check CSV file exists
        csv_path = tmp_path / "rfm_segments.csv"
        assert csv_path.exists()
        csv_df = pd.read_csv(csv_path)
        assert len(csv_df) == 3
        assert "Segment" in csv_df.columns


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_dataframe(self):
        """Test handling of empty dataframe."""
        empty_df = pd.DataFrame(columns=[
            "InvoiceNo", "InvoiceDate", "CustomerID", "Quantity", "UnitPrice"
        ])
        
        # compute_rfm should handle empty data, but groupby on empty will fail
        with pytest.raises((ValueError, KeyError, AssertionError)):
            compute_rfm(empty_df)
    
    def test_single_transaction_single_customer(self):
        """Test with absolute minimum data."""
        df = pd.DataFrame({
            "InvoiceNo": ["INV001"],
            "InvoiceDate": pd.to_datetime(["2011-12-01"]),
            "CustomerID": [1001],
            "Quantity": [1],
            "UnitPrice": [10.0],
            "Revenue": [10.0],
        })
        
        rfm = compute_rfm(df, snapshot_date=pd.Timestamp("2011-12-10"))
        # With only 1 customer, bins=5 will cause issues, use bins=1
        scored = score_rfm(rfm, bins=1)
        segmented = assign_segments(scored)
        
        # Should complete without error
        assert len(segmented) == 1
        assert segmented["Segment"].iloc[0] in {
            "VIP", "Loyal", "Growth Potential", "At Risk", "Dormant", "Mainstream"
        }
    
    def test_large_dataset_performance(self):
        """Test that functions handle larger datasets."""
        # Create a larger synthetic dataset
        n_customers = 1000
        n_transactions = 5000
        
        np.random.seed(42)
        base_date = pd.Timestamp("2011-01-01")
        df = pd.DataFrame({
            "InvoiceNo": [f"INV{i:05d}" for i in range(n_transactions)],
            "InvoiceDate": [
                base_date + pd.Timedelta(days=int(d)) 
                for d in np.random.randint(0, 365, n_transactions)
            ],
            "CustomerID": np.random.randint(1000, 1000 + n_customers, n_transactions),
            "Quantity": np.random.randint(1, 10, n_transactions),
            "UnitPrice": np.random.uniform(5, 100, n_transactions),
        })
        df["Revenue"] = df["Quantity"] * df["UnitPrice"]
        
        # Should complete in reasonable time
        rfm = compute_rfm(df, snapshot_date=pd.Timestamp("2012-01-01"))
        scored = score_rfm(rfm)
        segmented = assign_segments(scored)
        
        assert len(segmented) > 0
        assert len(segmented) <= n_customers


class TestIntegration:
    """Integration tests for full pipeline."""
    
    def test_full_pipeline(self, sample_transactions, tmp_path):
        """Test complete pipeline from load to segment."""
        # Save sample data
        data_path = tmp_path / "transactions.parquet"
        sample_transactions.to_parquet(data_path)
        
        # Run full pipeline
        df = load_transactions(data_path)
        rfm = compute_rfm(df, snapshot_date=pd.Timestamp("2011-12-10"))
        scored = score_rfm(rfm)
        segmented = assign_segments(scored)
        
        # Verify results
        assert len(segmented) == 3  # 3 unique customers
        assert "Segment" in segmented.columns
        assert segmented["Segment"].isin([
            "VIP", "Loyal", "Growth Potential", "At Risk", "Dormant", "Mainstream"
        ]).all()
