from tools.db_tools import get_connection
from tools.db_tools import get_available_rarities

def get_ancestries_with_descriptions():
    """Returns a list of ancestries with their descriptions."""
    rarities = get_available_rarities()
    query_string = "SELECT name, description FROM ancestries WHERE rarity IN ({})".format(",".join([f"'{rarity}'" for rarity in rarities]))
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query_string)
    ancestries = cursor.fetchall()
    conn.close()
    ancestries = [f"Ancestry: {ancestry[0]}\nDescription: {ancestry[1]}" for ancestry in ancestries]
    ancestries_string = "\n\n".join(ancestries)
    return ancestries_string

def get_classes_with_descriptions():
    """Returns a list of classes with their descriptions."""
    rarities = get_available_rarities()
    query_string = "SELECT name, description FROM classes WHERE rarity IN ({})".format(",".join([f"'{rarity}'" for rarity in rarities]))
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query_string)
    classes = cursor.fetchall()
    conn.close()
    classes = [f"Class: {each_class[0]}\nDescription: {each_class[1]}" for each_class in classes]
    classes_string = "\n\n".join(classes)
    return classes_string