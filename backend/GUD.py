#GUD.py
from flask import Flask, request, jsonify, session, Response, current_app, send_file, redirect, url_for

def get_entities(collection, entity_name, fields):
    entities = collection.stream()
    entity_list = [{**entity.to_dict(), "id": entity.id} for entity in entities]
    print(f"{entity_name} data:", entity_list)
    return jsonify({entity_name: entity_list})



def get_entity_by_id(collection, entity_name, fields, entity_id):
    entity = collection.document(entity_id).get()
    if entity.exists:
        entity_data = {field: entity.get(field) for field in fields}
        entity_data["id"] = entity_id  # Add the ID to the returned data
        print(f"{entity_name} data:", entity_data)
        return jsonify({entity_name: entity_data})
    else:
        return jsonify({"error": f"{entity_name} not found"}), 404

def add_entity(collection, data):
    collection.add(data)
    return jsonify({"message": f"Document added successfully"})


def delete_entity(collection, entity_id):
    entity = collection.document(entity_id).get()
    if entity.exists:
        collection.document(entity_id).delete()
        return jsonify({"message": f"Document with ID: {entity_id} deleted successfully"})
    else:
        return jsonify({"error": f"Document with ID: {entity_id} not found"}), 404

def update_entity(collection, entity_id, data):
    entity = collection.document(entity_id).get()
    if entity.exists:
        collection.document(entity_id).update(data)
        return jsonify({"message": f"Document with ID: {entity_id} updated successfully"})
    else:
        return jsonify({"error": f"Document with ID: {entity_id} not found"}), 404
