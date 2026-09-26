# Vireo Audio — Policy-derived constants and routing ownership
# All cost figures from support-policy.pdf v3.2, FY26 planning figures (§4)

CATEGORIES = [
    "Account & Login", "App & Firmware", "Audio Quality", "Billing & Payments",
    "Charging & Battery", "Connectivity", "Delivery & Shipping", "Other",
    "Product Enquiry", "Returns & Refunds", "Warranty & Repair",
]

# §6: Team ownership by category
CATEGORY_TO_TEAM = {
    "Billing & Payments": "Billing",
    "Delivery & Shipping": "Logistics",
    "Returns & Refunds": "Returns Desk",
    "Warranty & Repair": "Escalations & Warranty",
}
TEAM_TO_CATEGORY = {v: k for k, v in CATEGORY_TO_TEAM.items()}

# §2: Channel-to-frontline team mapping
CHANNEL_TO_FRONTLINE_TEAM = {
    "chat": "Chat Frontline",
    "social": "Chat Frontline",
    "email": "Email Frontline",
    "voice": "Voice Frontline",
}

# §3: First-response SLA targets (minutes)
SLA_MINUTES = {"chat": 15, "voice": 120, "social": 240, "email": 480}

# §4: Cost standards (FY26)
CONTACT_COST_INR = {"chat": 210, "email": 260, "voice": 520, "social": 240}
BLENDED_CONTACT_COST_INR = 290
TRANSFER_COST_INR = 305
SLA_BREACH_CREDIT_INR = 350       # §3: Auto-issued store credit per breach
AGENT_HOUR_COST_INR = 165         # §4: Fully loaded agent cost per hour

# §5: Replacement logistics cost
REPLACEMENT_SHIPPING_INR = 340    # Reverse pickup + forward shipping

# Business case targets
TARGET_HANDOFF_RATE = 0.134       # 20% relative reduction from ~16.8%
AUTO_ROUTE_CONFIDENCE = 0.70      # Confidence threshold for auto-routing
WEEKLY_TICKET_VOLUME = 650        # Client-stated weekly volume

# Headcount cost (from Arjun Mehta's email: "Two hires is about Rs 9 lakh a year")
HEADCOUNT_COST_TWO_HIRES_INR = 900_000
