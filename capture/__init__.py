"""Data capture and parsing."""
from capture.email_parser import parse_email, ParsedEmail
from capture.data_generator import generate_synthetic_dataset, get_sample_emails_for_demo

__all__ = ["parse_email", "ParsedEmail", "generate_synthetic_dataset", "get_sample_emails_for_demo"]
