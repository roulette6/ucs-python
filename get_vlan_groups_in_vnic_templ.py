"""
When you create a VLAN group and assign org permissions,
you can then add VLAN groups to a vNIC template within
an org with permission to use the VLAN group.

This script will create a dict of VLAN groups with a list
of the VLANs in those groups, as well as a list of the
references to those VLAN groups (fabricNetGroupRef) by
vNIC templates.
"""

from re import search
import sys
from ucsmsdk.ucshandle import UcsHandle


def main():

    # log into UCS and exit if there was a login issue
    handle = UcsHandle("ucs.vm.jm", "ucsro", "ucsro")
    if not handle.login():
        sys.exit("Invalid UCS handle. Please check FQDN and credentials")

    # get lists of objects needed and log out
    vlan_group_objects = handle.query_classid("fabricNetGroup")
    vlan_ref_objects = handle.query_classid("fabricPooledVlan")
    group_ref_objects = handle.query_classid("fabricNetGroupRef")
    handle.logout()

    # create dict of empty lists whose keys are the VLAN group names
    vlan_groups = get_vlan_group_names(vlan_group_objects)

    # get VLANs referenced in VLAN groups and update vlan_groups dict
    vlan_groups = add_vlans_to_groups(vlan_groups, vlan_ref_objects)

    # format dict of VLAN groups into a human readable str and print it
    print(
        "\n##### VLAN groups and their VLANs: #####",
        get_vlan_group_string(vlan_groups),
        sep="\n",
    )

    # format list of VLAN group references in vNIC templates and print it
    print(
        "##### vNIC template references: #####",
        get_vlan_group_ref_string(group_ref_objects),
        sep="",
    )


def get_vlan_group_names(vg_obj):
    """
    Returns a dict of empty lists whose keys are the VLAN group names

        Parameters:
            vg_obj (list): A list of VLAN group objects

        Returns:
            vlan_groups (dict): Dict of VLAN group names as keys
    """

    # create dict of VLAN groups with empty list of VLANs
    vlan_groups = {}
    for object in vg_obj:
        vlan_groups[object.name] = []

    return vlan_groups


def add_vlans_to_groups(vlan_groups, vlan_refs):
    """
    Returns a dict of lists whose keys are the VLAN group names and list
    values are the VLAN names referenced by that group

        Parameters:
            vlan_groups (dict): A dict of lists for updating
            vgvlan_refs (list): A list of VLAN ref objects

        Returns:
            vlan_groups (dict): Dict of VLAN groups and their VLANs
    """
    for vlan_ref in vlan_refs:
        # match the VLAN group name in the DN and add VLAN name to the
        # list whose key is the VLAN group name
        match = search(r"(?:net-group-)(?P<v_group>\w+)(?:\/)", vlan_ref.dn)

        if match:
            vlan_groups[match.group("v_group")].append(vlan_ref.name)

    return vlan_groups


def get_vlan_group_string(vlan_groups):
    """
    Returns a string of VLAN groups and their VLANs

        Parameters:
            vlan_groups (dict): A dict of lists such as the following:
            {"grp1": [vlan1, vlan2], "grp2": [vlan3, vlan4]}

        Returns:
            vg_string (str): String of VLAN groups and their VLANs
    """
    vg_string = ""
    for group, vlans in vlan_groups.items():
        # sort list of VLANs and build comma
        # separated string of VLAN names
        vlans.sort()
        vlan_names = ""

        for vlan in vlans[:-1]:
            vlan_names += f"{vlan}, "
        vlan_names += f"{vlans.pop()}"
        vg_string += f"VLAN group: {group}\nVLANs: {vlan_names}\n--\n"

    return vg_string


def get_vlan_group_ref_string(group_refs):
    """
    Returns a string of VLAN groups referenced by vNIC templates

        Parameters:
            group_refs (list): A list of VLAN group reference objects

        Returns:
            group_ref_string (str): String of vNIC templates and  VLAN
            group they reference
    """
    group_ref_string = ""
    for ref in group_refs:
        match = search(
            r"(?:lan-conn-templ-)(?P<vnic_template>\w+)(?:/)(?:net-group-ref-)(?P<vlan_group>\w+)",
            ref.dn,
        )
        if match:
            vlan_group_usage = (
                f"vNIC template {match.group('vnic_template')} "
                f"uses VLAN group {match.group('vlan_group')}\n--"
            )
            group_ref_string += f"\n{vlan_group_usage}"

    return group_ref_string


if __name__ == "__main__":
    main()
