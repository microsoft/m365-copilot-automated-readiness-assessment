"""
OneDrive for Business (Plan 2) - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name
from azure.core.exceptions import HttpResponseError

async def get_deployment_status(client):
    """
    Check OneDrive deployment and usage for Copilot readiness.
    
    API: GET /users?$select=id,displayName,userPrincipalName&$filter=assignedLicenses/any(x:x/skuId ne null)&$top=999
    Then check /users/{id}/drive for each user
    Permission: User.Read.All, Files.Read.All
    
    Checks:
    - Number of OneDrive drives provisioned
    - Active usage indicator for Copilot content access
    
    Args:
        client: Microsoft Graph client
        
    Returns:
        dict with deployment information or None if check fails
    """
    try:
        import asyncio
        
        # Get sample of users (first 100) to check OneDrive provisioning
        users = await client.users.get()
        
        provisioned_count = 0
        total_users = 0
        if users and users.value:
            total_users = len(users.value)
            
            # Check first 10 users for OneDrive (sampling) - IN PARALLEL
            async def check_user_drive(user):
                try:
                    drive = await client.users.by_user_id(user.id).drive.get()
                    return 1 if drive else 0
                except:
                    return 0  # User doesn't have OneDrive provisioned
            
            # Run all drive checks in parallel
            drive_checks = [check_user_drive(user) for user in users.value[:10]]
            results = await asyncio.gather(*drive_checks)
            provisioned_count = sum(results)
            
            # Estimate total based on sample
            if provisioned_count > 0:
                estimated_total = int((provisioned_count / min(10, total_users)) * total_users)
            else:
                estimated_total = 0
        else:
            estimated_total = 0
        
        return {
            'available': True,
            'provisioned_drives': estimated_total,
            'sampled': True
        }
    except HttpResponseError as e:
        if e.status_code == 401:
            return {'available': False, 'reason': 'Authentication failed (requires User.Read.All permission)'}
        if e.status_code == 403:
            return {'available': False, 'reason': 'Permission denied (requires User.Read.All permission)'}
        return {'available': False, 'reason': f'API error {e.status_code}'}
    except Exception as e:
        error_type = type(e).__name__
        return {'available': False, 'reason': f'{error_type}: Insufficient permissions'}

async def get_recommendation(sku_name, status="Success", client=None, m365_insights=None):
    """
    OneDrive for Business Plan 2 stores personal files that Copilot accesses
    to provide context-aware suggestions and content generation.
    
    Returns 2-3 recommendations:
    1. License status (active/inactive)
    2. Deployment status (drives provisioned, usage assessment)
    3. Usage insights (if m365_insights available) - NEW
    
    Args:
        sku_name: SKU name
        status: Provisioning status
        client: Optional Graph client
        m365_insights: Optional pre-computed M365 usage metrics
    
    Args:
        sku_name: SKU name where feature is found
        status: Provisioning status
        client: Optional Graph client for deployment check
    
    Returns:
        list: Two recommendation dicts [license_rec, deployment_rec]
    """
    feature_name = "OneDrive for Business (Plan 2)"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    # RECOMMENDATION 1: License Status
    if status == "Success":
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling Copilot to access personal file storage",
            recommendation="",
            link_text="OneDrive Documentation",
            link_url="https://learn.microsoft.com/onedrive/onedrive",
            status=status
        ))
    else:
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, restricting Copilot's access to personal documents",
            recommendation=f"Enable {feature_name} to ensure Copilot can find and use files stored in users' personal OneDrive. While SharePoint handles team content, OneDrive stores drafts, personal notes, and working documents that employees frequently reference. Copilot searches OneDrive to answer questions like 'Find my notes from the vendor meeting' or 'Use my proposal template to draft a new document.' Plan 2 provides unlimited storage and version history.",
            link_text="OneDrive as Copilot Data Source",
            link_url="https://learn.microsoft.com/onedrive/onedrive",
            priority="Medium",
            status=status
        ))
    
    # RECOMMENDATION 2: Deployment Check (only if license is active)
    if status == "Success":
        deployment_data = None
        if client:
            deployment_data = await get_deployment_status(client)
        
        if deployment_data and deployment_data.get('available'):
            drive_count = deployment_data.get('provisioned_drives', 0)
            is_sampled = deployment_data.get('sampled', False)
            
            if drive_count > 50:
                # GOOD: Substantial OneDrive adoption
                count_text = f"~{drive_count}" if is_sampled else str(drive_count)
                recommendations.append(new_recommendation(
                    service="M365",
                    feature="OneDrive Content Deployment",
                    observation=f"{count_text} OneDrive drive(s) provisioned with personal content available for Copilot",
                    recommendation="",
                    link_text="OneDrive Admin Center",
                    link_url="https://admin.microsoft.com/onedrive",
                    status="Success"
                ))
            elif drive_count > 10:
                # MODERATE: Some adoption but could improve
                count_text = f"~{drive_count}" if is_sampled else str(drive_count)
                recommendations.append(new_recommendation(
                    service="M365",
                    feature="OneDrive Content Deployment",
                    observation=f"Only {count_text} OneDrive drive(s) provisioned - moderate user adoption. Expand OneDrive deployment to provide Copilot with personal work context for better document recommendations and file organization.",
                    recommendation=f"Increase OneDrive adoption to improve Copilot's access to personal work files. Encourage users to migrate documents from local drives, email attachments, and network shares to OneDrive. This makes personal drafts, templates, and working documents accessible to Copilot while maintaining individual ownership and permissions. Greater OneDrive usage means Copilot can find more relevant files when users ask questions or request document generation.",
                    link_text="Drive OneDrive Adoption",
                    link_url="https://learn.microsoft.com/onedrive/plan-onedrive-enterprise",
                    priority="Medium",
                    status="Warning"
                ))
            else:
                # LOW: Minimal adoption
                count_text = f"~{drive_count}" if is_sampled else str(drive_count)
                recommendations.append(new_recommendation(
                    service="M365",
                    feature="OneDrive Content Deployment",
                    observation=f"Only {count_text} OneDrive drive(s) provisioned - minimal user adoption limits Copilot effectiveness",
                    recommendation=f"IMPORTANT: Drive OneDrive adoption across your organization. Low OneDrive usage means Copilot cannot access most users' personal files, templates, and working documents. Launch adoption campaigns encouraging users to move files from local drives, desktops, and email to OneDrive. Provide training on OneDrive benefits (anywhere access, version history, auto-save). Set up folder redirection for Desktop/Documents. Higher OneDrive adoption = more content for Copilot = better AI assistance.",
                    link_text="OneDrive Adoption Guide",
                    link_url="https://learn.microsoft.com/onedrive/plan-onedrive-enterprise",
                    priority="High",
                    status="Warning"
                ))
        elif deployment_data and not deployment_data.get('available'):
            # Could not verify - show actionable guidance
            recommendations.append(new_recommendation(
                service="M365",
                feature="OneDrive Content Deployment",
                observation=f"OneDrive license is active in {friendly_sku}. Usage assessment requires manual verification.",
                recommendation=f"Assess OneDrive adoption rates for Copilot readiness. Check how many users have provisioned OneDrive and are actively storing files. Low adoption limits Copilot's ability to access personal documents, templates, and drafts. Encourage migration from local drives and network shares. Monitor usage through OneDrive admin reports.",
                link_text="OneDrive Admin Center",
                link_url="https://admin.microsoft.com/onedrive",
                priority="Medium",
                status="PendingInput"
            ))
        else:
            # No client provided - show actionable guidance
            recommendations.append(new_recommendation(
                service="M365",
                feature="OneDrive Content Deployment",
                observation=f"OneDrive license is active in {friendly_sku}. Adoption assessment requires manual review.",
                recommendation=f"Review OneDrive adoption and usage patterns for Copilot optimization. Higher OneDrive usage means more personal files accessible to Copilot for better responses. Assess user provisioning, storage consumption, and file counts. Drive adoption through training, folder redirection policies, and migration tools. Personal files in OneDrive expand Copilot's knowledge base beyond SharePoint team content.",
                link_text="OneDrive Usage Reports",
                link_url="https://admin.microsoft.com/onedrive",
                priority="Medium",
                status="PendingInput"
            ))
    
    # NEW: OneDrive Usage Insights
    if status == "Success" and m365_insights and m365_insights.get('onedrive_report_available'):
        total_accounts = m365_insights.get('onedrive_total_accounts', 0)
        active_accounts = m365_insights.get('onedrive_active_accounts', 0)
        adoption_rate = m365_insights.get('onedrive_adoption_rate', 0)
        storage_gb = m365_insights.get('onedrive_storage_gb', 0)
        
        if adoption_rate >= 70:
            recommendations.append(new_recommendation(
                service="M365",
                feature=f"{feature_name} - Adoption",
                observation=f"Strong OneDrive adoption: {adoption_rate}% of {total_accounts} accounts active, {storage_gb:.1f} GB stored. Personal files accessible to Copilot",
                recommendation="",
                link_text="OneDrive Reports",
                link_url="https://learn.microsoft.com/microsoft-365/admin/activity-reports/onedrive-for-business-usage",
                status="Success"
            ))
        elif adoption_rate >= 30:
            recommendations.append(new_recommendation(
                service="M365",
                feature=f"{feature_name} - Adoption",
                observation=f"Moderate OneDrive adoption: {adoption_rate}% active ({active_accounts}/{total_accounts} accounts). Some personal content accessible to Copilot",
                recommendation="Increase OneDrive adoption for better Copilot personal file access. Migrate My Documents, Desktop, Pictures to OneDrive. More files in OneDrive = better Copilot context",
                link_text="OneDrive Adoption",
                link_url="https://adoption.microsoft.com/onedrive/",
                priority="Low",
                status="Success"
            ))
        else:
            recommendations.append(new_recommendation(
                service="M365",
                feature=f"{feature_name} - Adoption",
                observation=f"Low OneDrive adoption: Only {adoption_rate}% active. Limited personal files for Copilot access",
                recommendation="Deploy OneDrive folder redirection and Known Folder Move to increase adoption. Low usage limits Copilot's personal context",
                link_text="OneDrive Deployment",
                link_url="https://learn.microsoft.com/onedrive/redirect-known-folders",
                priority="Medium",
                status="Warning"
            ))

    return recommendations
