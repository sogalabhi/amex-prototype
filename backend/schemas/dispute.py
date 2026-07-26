from pydantic import BaseModel
from typing import Optional
from enum import Enum


class DocumentType(str, Enum):
    ORDER_RECEIPT = "order_receipt"
    DELIVERY_CONFIRMATION = "delivery_confirmation"
    CHAT_LOG = "chat_log"
    POLICY = "policy"
    PRODUCT_DESCRIPTION = "product_description"
    MERCHANT_PHOTOS = "merchant_photos"


class Transaction(BaseModel):
    txn_id: str
    amount: float
    currency: str
    date: str
    merchant: str
    descriptor: str
    channel: str
    shipping_address_on_order: Optional[str] = None


class CardmemberClaim(BaseModel):
    filed_date: str
    text: str


class MerchantDocument(BaseModel):
    doc_id: str
    type: DocumentType
    content: str


class GroundTruth(BaseModel):
    reason_code: str
    expected_outcome: str
    why: Optional[str] = None


class DisputeCase(BaseModel):
    case_id: str
    transaction: Transaction
    cardmember_claim: CardmemberClaim
    merchant_evidence: list[MerchantDocument]
    ground_truth: Optional[GroundTruth] = None
