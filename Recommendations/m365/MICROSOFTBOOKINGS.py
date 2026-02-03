"""
Microsoft Bookings - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Microsoft Bookings provides appointment scheduling that agents can
    automate for customer meetings and service bookings.
    """
    feature_name = "Microsoft Bookings (Service)"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    if status == "Success":
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling agent-automated appointment scheduling",
            recommendation="",
            link_text="Automate Scheduling with Agents",
            link_url="https://learn.microsoft.com/microsoft-365/bookings/",
            status=status
        ))
    else:
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, preventing automated appointment management",
            recommendation=f"Enable {feature_name} to let conversational agents handle appointment scheduling through natural language. Build agents that book consultations, reschedule meetings based on conflicts, send automated reminders, and handle cancellations - all through chat interfaces. Bookings with agent integration eliminates scheduling friction for customer-facing teams, healthcare providers, and professional services, improving booking conversion while reducing administrative burden.",
            link_text="Automate Scheduling with Agents",
            link_url="https://learn.microsoft.com/microsoft-365/bookings/",
            priority="Low",
            status=status
        ))
    
    # NEW: Usage Context based on email and Teams activity
    if status == "Success" and m365_insights and m365_insights.get('email_report_available'):
        avg_emails = m365_insights.get('email_avg_sent_per_user', 0)
        total_meetings = m365_insights.get('teams_total_meetings', 0)
        
        if avg_emails >= 10 and total_meetings >= 500:
            # High email + meetings = strong scheduling/booking context
            recommendations.append(new_recommendation(
                service="M365",
                feature="Microsoft Bookings (Service)",
                observation=f"Your users average {avg_emails:.1f} emails per user and conduct {total_meetings} Teams meetings. This high communication volume suggests strong opportunities for Microsoft Bookings to streamline appointment scheduling for customer-facing teams, reducing email back-and-forth for booking coordination.",
                recommendation="",  # No recommendation - this is helpful context
                link_text="",
                link_url="",
                priority="",
                status=""
            ))
        elif avg_emails >= 5 or total_meetings >= 100:
            # Moderate activity = suggest Bookings for specific teams
            recommendations.append(new_recommendation(
                service="M365",
                feature="Microsoft Bookings (Service)",
                observation=f"Your users average {avg_emails:.1f} emails per user with {total_meetings} Teams meetings. Consider deploying Microsoft Bookings for teams that handle external appointments (sales, support, healthcare, consulting) to reduce scheduling overhead.",
                recommendation=f"Pilot Microsoft Bookings with customer-facing teams. With {avg_emails:.1f} emails per user and {total_meetings} meetings, your organization has scheduling activity that could benefit from self-service booking pages. Start with sales or customer success teams to eliminate email back-and-forth for appointment scheduling, improving customer experience and team productivity.",
                link_text="Deploy Microsoft Bookings",
                link_url="https://learn.microsoft.com/microsoft-365/bookings/get-access",
                priority="Low",
                status="PendingInput"
            ))
        else:
            # Low communication activity
            recommendations.append(new_recommendation(
                service="M365",
                feature="Microsoft Bookings (Service)",
                observation=f"Low communication activity: {avg_emails:.1f} emails per user and {total_meetings} meetings. Limited scheduling context for Bookings - establish meeting culture where Copilot can automate scheduling and meeting prep.",
                recommendation="Build email and Teams adoption before deploying Microsoft Bookings. Focus on increasing collaboration activity first. Bookings value grows with communication volume.",
                link_text="Microsoft 365 Adoption",
                link_url="https://adoption.microsoft.com/",
                priority="Low",
                status="Success"
            ))

    return recommendations
