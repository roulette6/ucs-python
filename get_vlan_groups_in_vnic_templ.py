"""
When you create a VLAN group and assign org permissions,
you can then add VLAN groups to a vNIC template within
an org with permission to use the VLAN group.

This script will create a dict of VLAN groups with a list
of the VLANs in those groups, as well as a list of the
references to those VLAN groups (fabricNetGroupRef) by
vNIC templates.
"""


def main():
    import re
    import sys
    from ucsmsdk.ucshandle import UcsHandle

    # log into UCS
    handle = UcsHandle("ucs.vm.jm", "ucsro", "ucsro")

    # get dict of empty lists whose key is the VLAN group name
    vlan_groups = get_vlan_group_names(handle)

    # get VLANs referenced in VLAN groups
    vlan_ref_objects = handle.query_classid("fabricPooledVlan")

    # add VLAN names to list whose key is their VLAN group
    for object in vlan_ref_objects:
        # match the VLAN group name in the DN
        match = re.search(r"(?:net-group-)(?P<v_group>\w+)(?:\/)", object.dn)

        # if there's a match, add the VLAN name to the list whose key
        # is the VLAN group name
        if match:
            vlan_groups[match.group("v_group")].append(object.name)

    # print the dict of lists with leading empty line to
    # separate output from CLI command
    print()
    for group, vlans in vlan_groups.items():
        # sort list of VLANs and build comma
        # separated string of VLAN names
        vlans.sort()
        vlan_names = ""

        for vlan in vlans[:-1]:
            vlan_names += f"{vlan}, "
        vlan_names += f"{vlans.pop()}"
        print(f"VLAN group: {group}", f"VLANs: {vlan_names}", sep="\n", end="\n\n")

    group_ref_objects = handle.query_classid("fabricNetGroupRef")

    for object in group_ref_objects:
        match = re.search(
            r"(?:lan-conn-templ-)(?P<vnic_template>\w+)(?:/)(?:net-group-ref-)(?P<vlan_group>\w+)",
            object.dn,
        )
        if match:
            vlan_group_usage = (
                f"vNIC template {match.group('vnic_template')} "
                f"uses VLAN group {match.group('vlan_group')}\n--"
            )
            print(vlan_group_usage)

    handle.logout()


def get_vlan_group_names(ucs_handle):
    """
    Returns a dict of empty lists whose keys are the VLAN group names

        Parameters:
            ucs_handle (obj): A handle for a UCS session

        Returns:
            vlan_groups (dict): Dict of VLAN group names as keys
    """

    if not ucs_handle.login():
        sys.exit("Invalid UCS handle. Please check FQDN and credentials")

    # create dict of VLAN groups with empty list of VLANs
    vlan_groups = {}
    vlan_group_objects = ucs_handle.query_classid("fabricNetGroup")

    for object in vlan_group_objects:
        vlan_groups[object.name] = []

    return vlan_groups


if __name__ == "__main__":
    main()
