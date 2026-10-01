"""
Processor module for generating and exporting recommendations.
This module takes the collected service data and handles recommendation aggregation and export.
"""
from .export_recommendations import export_to_csv, export_to_excel, print_recommendations_summary


def collect_all_recommendations(m365_recommendations, entra_info, purview_info, 
                                defender_info, power_platform_info, copilot_studio_info,
                                a365_info):
    """Collect all recommendations from different services."""
    all_recommendations = []
    all_recommendations.extend(m365_recommendations)
    all_recommendations.extend(entra_info.get('recommendations', []))
    all_recommendations.extend(purview_info.get('recommendations', []))
    all_recommendations.extend(defender_info.get('recommendations', []))
    all_recommendations.extend(power_platform_info.get('recommendations', []))
    all_recommendations.extend(copilot_studio_info.get('recommendations', []))
    all_recommendations.extend(a365_info.get('recommendations', []))

    # Final safety net: a recommendation module that unexpectedly falls through
    # without an explicit return (as MIP_S_CLP1 once did) would silently append
    # None here. Drop any such entries so export never crashes on them, even if
    # a future module reintroduces that bug (the individual append sites above
    # already guard against this too - this is defense in depth).
    all_recommendations = [rec for rec in all_recommendations if rec is not None]

    return all_recommendations


def process_and_print_all_information(m365_result, entra_info, 
                                      purview_info, defender_info, power_platform_info, 
                                      copilot_studio_info, a365_info):
    """Process all service information and generate recommendations."""
    # Unpack M365 results
    (m365_info, m365_recommendations) = m365_result
    
    print("\n" + "="*80)
    
    # Collect all recommendations
    all_recommendations = collect_all_recommendations(
        m365_recommendations, entra_info, purview_info, 
        defender_info, power_platform_info, copilot_studio_info, a365_info
    )
    
    # Print and export recommendations
    if all_recommendations:
        csv_path = export_to_csv(all_recommendations)
        excel_path = export_to_excel(all_recommendations)
        print_recommendations_summary(all_recommendations, csv_path, excel_path)
    else:
        print_recommendations_summary(all_recommendations)
    
    print("\n" + "="*80)
