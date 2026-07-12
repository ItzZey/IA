from typing import Any


def build_alerts(analysis: dict[str, Any]) -> list[dict[str, Any]]:
    alerts: list[dict[str, Any]] = []
    details = analysis["details"]
    price = analysis["price"]
    levels = analysis["levels"]
    dividend = details["dividend"]
    technical = details["technical"]

    if levels["entry_zone_low"] <= price <= levels["entry_zone_high"]:
        alerts.append({"type": "price", "severity": "medium", "message": "Prix dans la zone d'entree theorique"})
    if technical["rsi"] > 75:
        alerts.append({"type": "technical", "severity": "medium", "message": "RSI surachete"})
    if technical["rsi"] < 30:
        alerts.append({"type": "technical", "severity": "medium", "message": "RSI survendu"})
    if dividend["payout_ratio"] > 60:
        alerts.append({"type": "dividend", "severity": "high", "message": "Payout ratio a examiner avec prudence"})
    for risk in details["risk"]["risks"]:
        alerts.append({"type": "risk", "severity": "medium", "message": risk})
    return alerts
