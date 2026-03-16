# -*- coding: utf-8 -*-
import subprocess
import time

import py2neo
import unidecode
from py2neo import Graph

from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
from custom_libs.toth import acutes_filter
from custom_libs.toth import defs as d

graph = Graph(
    NEO4J_URI,
    auth=(NEO4J_USER, NEO4J_PASSWORD)
)


def execute_query(query, values=None):
    try:
        if values is not None:
            complete_query = query % values
        else:
            complete_query = query
        graph = database_connection_test()
        return graph.run(complete_query)
    except Exception as error:
        print('*' * 100)
        print('QUERY', query)
        print('VALUES', values)
        print('*' * 100)
        raise error


def execute_query_search(query, values=None):
    try:
        graph = database_connection_test()
        return graph.run(query, parameters=values or {})
    except Exception as error:
        print('*' * 100)
        print('QUERY', query)
        print('VALUES', values)
        print('*' * 100)
        raise error


def shutdown_neo4j():
    subprocess.call(neo4j_path % "stop", shell=True)
    print("trying to execute:", neo4j_path % "start")


def database_connection_test(prints=False):
    if prints:
        print('=' * 100)
    try:
        graph = py2neo.Graph(host=HOST, user=USER, password=PASS)
        if graph:
            if prints:
                print("databases is working...")
            return graph
    except Exception as err:
        print(unidecode.unidecode(str(err)))
        try:
            print("trying to execute:", neo4j_path % "start")
            subprocess.call(neo4j_path % "start", shell=True)
            for x in range(0, 11):
                bar = '=' * x
                print('\rwaiting for server delay', '[', bar.ljust(10), ']', )
                time.sleep(1)
            graph = py2neo.Graph(GRAPH)
            return graph
        except Exception as err:
            print("subprocess ERROR:", unidecode.unidecode(str(err)))
            raise err
    finally:
        if prints:
            print('=' * 100)


def get_node(nid, label=None):
    if label is None:
        query = """MATCH (n) WHERE n.nid="%s" RETURN n;""" % nid
    else:
        query = """MATCH (n:%s) WHERE n.nid="%s" RETURN n;""" % (label, nid)
    node = execute_query(query)
    return node.evaluate()


def get_nodes(nid, label=None):
    if label is None:
        query = """MATCH (n) WHERE n.nid="%s" RETURN n;""" % nid
    else:
        query = """MATCH (n:%s) WHERE n.nid="%s" RETURN n;""" % (label, nid)
    result = execute_query(query)
    return result


def verify_node_oneness(nid, label):
    query = """MATCH (n:%s) WHERE n.nid="%s" RETURN n;""" % (label, nid)
    cursor = execute_query(query)
    if len(cursor.data()) == 1:
        return True
    else:
        return False


def create_tense_relationship(n1, n2, relation):
    query = """
            MATCH (n1:%s {nid:"%s"}), (n2:%s {nid:"%s"})
            CREATE (n1)-[:%s]->(n2);
            """ % (d.VERBO, n1, d.CONJUGACAO, n2, relation)
    return execute_query(query).evaluate()


def remove_relationship(word):
    query = """
            MATCH (n1{nid:'%s'})<-[r:SEMANTICS]-(n2) DELETE r;
            """ % word
    print("Relationship Removed for (%s)" % word)
    return execute_query(query).evaluate()


def get_relationships(n1, n2, rel):
    query = """
    MATCH (n{nid:"%s"})-[r:%s]->(m{nid:"%s"}) RETURN r;
    """ % (n1, rel, n2)
    return [r for r in execute_query(query)]


def set_relationship_count(n1, n2, rel, counter):
    query = """
    MATCH (n{nid:"%s"})-[r:%s]-(b {nid:"%s"})
    SET r.count = %s
    """ % (n1, rel, n2, counter)
    execute_query(query)


def relationship_incremental_count(n1, n2, rel):
    if check_rel_between_nodes(n1, n2, rel) == 0:
        create_relationship(n1, n2, rel)
        set_relationship_count(n1, n2, rel, 0)
    relation = get_relationships(n1, n2, rel)
    if len(relation) == 1:
        current_count = relation[0]['r'].properties['count']
        new_count = current_count + 1
        set_relationship_count(n1, n2, rel, new_count)
        return True
    else:
        return False


def create_relationship(n1, n2, rel):
    if check_rel_between_nodes(n1, n2, rel) == 0:
        result_1 = execute_query("""MATCH (n) WHERE n.nid="%s" RETURN n;""" % n1).evaluate()
        result_2 = execute_query("""MATCH (n) WHERE n.nid="%s" RETURN n;""" % n2).evaluate()
        if result_1 and result_2:
            query = """
                MATCH (n1 {nid:"%s"}), (n2 {nid:"%s"})
                CREATE (n1)-[:%s]->(n2);
                """ % (n1, n2, rel)
            # print("Relationship Created (%s)--[:%s]-->(%s) \o/" % (n1, rel, n2))
            return execute_query(query).evaluate()
        else:
            if not result_1 and result_2:
                print("%s is not in DB" % n1)
                not_in_db(n1)
            elif not result_2 and result_1:
                print("%s is not in DB" % n2)
                not_in_db(n2)
            elif not result_1 and not result_2:
                print("%s and %s are not in DB" % (n1, n2))
                not_in_db(n1)
                not_in_db(n2)
            else:
                print("Fuck it!: %s, %s" % (n1, n2))
    else:
        print("Relationship already Exists (%s)--[:%s]-->(%s)" % (n1, rel, n2))


def create_relationship_synonym(n1, n2, label):
    if check_rel_between_nodes(n1, label, n2) == 0:
        result_1 = execute_query("""MATCH (n) WHERE n.nid="%s" RETURN n;""" % n1).evaluate()
        result_2 = execute_query(""""MATCH (n) WHERE n.nid="%s" RETURN n;""" % n2).evaluate()
        if result_1 and result_2:
            query = """
                MATCH (n1 {nid:"%s"}), (n2 {nid:"%s"})
                CREATE (n1)-[:%s]->(n2);
                """ % (n1, label, n2)
            return execute_query(query).evaluate()
        else:
            if not result_1 and result_2:
                print("%s is not in DB" % n1)
                not_in_db(n1)
            elif not result_2 and result_1:
                print("%s is not in DB" % n2)
                not_in_db(n2)
            elif not result_1 and not result_2:
                print("%s and %s are not in DB" % (n1, n2))
                not_in_db(n1)
                not_in_db(n2)
            else:
                print("Error!: %s, %s" % (n1, n2))
    else:
        print("Relationship already Exists (%s)--[:synonym]-->(%s)" % (n1, n2))


def create_semantic_relationship(n1, n2, rel_label, node_type=None):
    try:
        if check_rel_between_nodes(n1, n2, rel_label) == 0:
            if node_type is not None:
                result_1 = execute_query("""MATCH (n:%s) WHERE n.nid="%s" RETURN n;""" % (node_type, n1)).evaluate()
                result_2 = execute_query("""MATCH (n:%s) WHERE n.nid="%s" RETURN n;""" % (node_type, n2)).evaluate()
            else:
                result_1 = execute_query("""MATCH (n) WHERE n.nid="%s" RETURN n;""" % n1).evaluate()
                result_2 = execute_query("""MATCH (n) WHERE n.nid="%s" RETURN n;""" % n2).evaluate()

            if result_1 and result_2:
                if node_type is not None:
                    query = """
                        MATCH (n1:%s {nid:"%s"}) OPTIONAL MATCH (n2:%s {nid:"%s"})
                        CREATE (n1)-[:%s]->(n2);
                        """ % (node_type,
                               str(acutes_filter.ascii_2_portuguese(n1)),
                               node_type,
                               str(acutes_filter.ascii_2_portuguese(n2)),
                               d.R_SEMANTIC_FIELD)
                else:
                    query = """
                        MATCH (n1 {nid:"%s"}) OPTIONAL MATCH (n2 {nid:"%s"})
                        CREATE (n1)-[:%s]->(n2);
                        """ % (str(acutes_filter.ascii_2_portuguese(n1)),
                               str(acutes_filter.ascii_2_portuguese(n2)),
                               d.R_SEMANTIC_FIELD)
                print("creating relation", n1, n2)
                return execute_query(str(query)).evaluate()
            else:
                if not result_1 and result_2:
                    print("%s is not in DB" % n1)
                    not_in_db(n1)
                elif not result_2 and result_1:
                    print("%s is not in DB" % n2)
                    not_in_db(n2)
                elif not result_1 and not result_2:
                    print("%s and %s are not in DB" % (n1, n2))
                    not_in_db(n1)
                    not_in_db(n2)
                else:
                    print("Error!: %s, %s" % (n1, n2))
        else:
            print("Relationship already Exists (%s)--[:SEMANTICS]-->(%s)" % (n1, n2))
    except Exception as err:
        print('-' * 100)
        print(err)  # , n1, n2, rel_label, node_type


def check_rel_between_nodes(n1, n2, rel=None):
    if rel is not None:
        query = """
            MATCH (n{nid:"%s"})-[r:%s]-(m{nid:"%s"}) RETURN SIGN(COUNT(r));
            """ % (n1, rel, n2)
    else:
        query = """
            MATCH (n{nid:"%s"})-[r]-(m{nid:"%s"}) RETURN SIGN(COUNT(r));
            """ % (n1, n2)
    return execute_query(query).evaluate()


def not_in_db(word):
    file_content = open('not_in_db.txt', 'r')
    content = file_content.read()
    file_content.close()
    if word not in content:
        f = open('not_in_db.txt', 'a')
        f.write(word + '\n')
        f.close()


def remove_relationship_overly_semantics(frag):
    query = """
            MATCH (n1)<-[r:SEMANTICS]-(n2) WHERE n1.nid=~"%s.+?" DELETE r;
            """ % frag
    print("Relationships Removed for frag (%s)" % frag)
    return execute_query(query).evaluate()


def get_nodes_nids_by_regex(expression, label=None):
    if label is None:
        query = """MATCH (n) WHERE n.nid=~"%s" AND NOT n:not_in_web AND NOT n:Conjugacao RETURN n;""" % expression
    else:
        query = """MATCH (n:%s) WHERE n.nid=~"%s" AND NOT n:not_in_web AND NOT n:Conjugacao RETURN n;""" % (
            label, expression)
    cursor = execute_query(query)
    buffer_nodes = list()

    while True:
        node = cursor.evaluate()
        if node is not None:
            buffer_nodes.append(node)
        else:
            break
    cursor.close()
    return buffer_nodes


def create_tense(tense):
    query = "CREATE (n:Conjugacao{nid:\"%s\"}) RETURN n;" % tense
    return execute_query(query).evaluate()


def get_conjugation_root(term):
    query = """MATCH (c:Conjugacao) WHERE c.nid="%s" OPTIONAL MATCH (c)-[r]-(v) RETURN c,r,v;""" % term
    # .data()[0]
    return execute_query(query)


def delete_conjugation_rel(term):
    query = """MATCH (c:Conjugacao) WHERE c.nid="%s" OPTIONAL MATCH (c)-[r]-(v) DELETE r;""" % term
    return execute_query(query)


def delete_conjugation_wrong(term):
    delete_query = """MATCH (c:Conjugacao) WHERE c.nid="%s" OPTIONAL MATCH (c)-[r]-(v) DELETE r;""" % term
    execute_query(delete_query)
    query = """MATCH (c:Conjugacao) WHERE c.nid="%s" DELETE c;""" % term
    execute_query(query)


def add_property(node_id, prop, value):
    if isinstance(value, str):
        value = "\"" + value + "\""
    if isinstance(value, set):
        value = list(value)
    if isinstance(value, list):
        value = str(value)
    query = """MATCH (n {nid:'%s'}) SET n.%s = %s RETURN n;"""
    execute_query(query % (node_id, prop, value))


def remove_property(node_id, prop):
    query = """MATCH (n { nid: '%s' }) REMOVE n.%s RETURN n;"""
    execute_query(query % (node_id, prop))


def add_label(node_id, new_label):
    query = """MATCH (n {nid:'%s'}) SET n:%s RETURN n;"""
    execute_query(query % (node_id, new_label))


def remove_label(node_id, old_label):
    query = """MATCH (n { nid: '%s' }) REMOVE n:%s RETURN n;"""
    execute_query(query % (node_id, old_label))


def create_node(node_id, node_type, additional_params=None):
    additional_params_buffer = ''
    if additional_params is not None:
        for i, pair in enumerate(additional_params.items()):
            additional_params_buffer += pair[0] + ': "' + str(pair[1]) + '"'
            if i + 1 != len(additional_params):
                additional_params_buffer += ', '
        query_find = """MATCH (n:%s {nid: "%s", %s}) RETURN n;"""
        result = list(execute_query(query=query_find, values=(node_type, node_id, additional_params_buffer)))
    else:
        query_find = """MATCH (n:%s {nid: "%s"}) RETURN n;"""
        result = list(execute_query(query=query_find, values=(node_type, node_id)))

    if len(result) == 0:
        if additional_params_buffer:
            query = """CREATE (:%s {nid: "%s", %s});"""
            execute_query(query=query, values=(node_type, node_id, additional_params_buffer))
        else:
            query = """CREATE (:%s {nid: "%s"});"""
            execute_query(query=query, values=(node_type, node_id))

        query_find = """MATCH (n:%s {nid: "%s"}) RETURN n;"""
        new_node = execute_query(query=query_find, values=(node_type, node_id))
        return new_node.evaluate()
    else:
        print("DUPLICATE NODES -> REPORT: %s" % str(result))
        return None


def count_pattern(reg_ex):
    query = """MATCH (n) WHERE n.nid=~"%s" RETURN COUNT(n);""" % reg_ex
    return execute_query(query).evaluate()


def check_word_type(word, labels):
    if isinstance(labels, str):
        labels = [labels]
    elif not isinstance(labels, list):
        raise Exception('Return dosen\'t match expected Type. IN: check_word_type()')
    query = """MATCH(n{nid: "%s"}) RETURN labels(n) AS label;""" % word
    result = execute_query(query).data()
    word_labels = [list(label['label'])[0] for label in result]

    if len([w for w in labels if w in word_labels]) > 0:
        return True
    else:
        return False


def get_word_type(word):
    if word.endswith('s'):
        word = word[:-1]
    query = """MATCH (n) WHERE n.nid =~ "%s[s]?" RETURN labels(n) AS label;
        """ % word
    result = execute_query(query).data()
    word_labels = list(set([list(label['label'])[0] for label in result]))
    return word_labels


def get_semantic_fields_to_word(word):
    query = """
            MATCH (n1:Substantivo{nid:"%s"})<-[:SEMANTICS]-(m)
            WITH m MATCH (m)--(x)--(n2:Substantivo{nid:"%s"}) RETURN x.nid,m.nid;
            """ % (word, word)
    result = execute_query(query)
    aggregate = dict()
    for rel in result.data():
        if not [True for g in aggregate.items() if rel['m.nid'] in g[1]]:
            if rel['m.nid'] not in aggregate.keys():
                aggregate[rel['m.nid']] = list()
            aggregate[rel['m.nid']].append(rel['x.nid'])
    return [list(set(d[1])) for d in aggregate.items()]


def buffer_exclusion_labels(node_form, exclude_labels):
    query_part = ""
    for label in exclude_labels:
        query_part += "NOT %s:%s AND " % (node_form, label)
    print(query_part)
    return query_part


def find_by_plural(plural, exclude_labels=None):
    query = """MATCH (n) WHERE n.plural='%s' RETURN n""" % plural
    if exclude_labels is not None:
        if isinstance(exclude_labels, list):
            buffered_options = buffer_exclusion_labels('n', exclude_labels)
            query = """MATCH (n) WHERE %s n.plural='%s' RETURN n""" % (buffered_options, plural)
        else:
            query = """MATCH (n) WHERE NOT n:%s AND n.plural='%s' RETURN n""" % (exclude_labels, plural)
    result = execute_query(query)
    return result.evaluate()


def get_synonymous_list(word, exclude_labels=None):
    print(exclude_labels)
    query = """
            MATCH (n{nid:"%s"}:Substantivo)-[r:SYNONYMOUS]->(m:Substantivo)
            RETURN m.nid;
            """ % word
    result = execute_query(query)
    return result


def add_label_to_node(node, label):
    query = """
            MATCH (n{nid: '%s'}) SET n:%s RETURN n
            """ % (node, label)
    result = execute_query(query)
    print("Label \"%s\" setted for (%s)" % (label, node))
    return result


def remove_label_of_node(node, label):
    query = """
            MATCH (n{nid: '%s'}) REMOVE n:%s RETURN n
            """ % (node, label)
    result = execute_query(query)
    return result


def get_semantic_fields_to_word_without_proper(word, prop):
    query = """
            MATCH (n{nid:"%s"})<-[:SEMANTIC_FIELD]-(m)
            WHERE NOT EXISTS(m.%s)
            RETURN m.nid;
            """ % (word, prop)
    result = execute_query(query)
    aggregate = set()
    data = result.data()
    if data:
        for r in data:
            aggregate.add(r['m.nid'])
    return list(aggregate)


def search_requirements(term):
    query = """
    MATCH (n:TechTerm)-[r:REQUIREMENT]-(m:TechTerm) WHERE n.nid = '%s' 
    RETURN r.count, m.nid ORDER BY r.count DESC LIMIT 10;
    """ % term
    results = execute_query(query).data()
    treated = list()
    if results is not None:
        for r in results:
            treated.append({'nid': r['m.nid'], 'count': r['r.count']})
    return treated


def avg_salary_with_two_terms(n1, n2):
    query = """
        MATCH (n{nid: '%s'})-[]-(j:JOB)-[]-(m{nid: '%s'})
        WITH j MATCH (j)--(s:SalaryRange) WHERE EXISTS(s.value) RETURN avg(toInt(s.value)) AS avg;
    """ % (n1, n2)
    results = execute_query(query).data()
    return results[0]['avg']


def search_jobs(search_terms):
    query = """
            MATCH (j:JOB)
            WHERE j.description IS NOT NULL

            WITH j, $search_terms AS search_terms
            UNWIND search_terms AS term

            WITH j, term
            WHERE toLower(j.description) CONTAINS term

            WITH j, collect(DISTINCT term) AS matched_terms
            WITH j, matched_terms,
                 size(matched_terms) AS matched_count,
                 size($search_terms) AS total_terms
            WHERE matched_count > 0

            WITH j, matched_terms, matched_count,
                 toFloat(matched_count) / toFloat(total_terms) AS match_rate

            RETURN
                j.site AS site,
                j.link AS link,
                j.salary AS salary,
                j.description AS description,
                matched_terms AS matches,
                match_rate,
                matched_count
            ORDER BY matched_count DESC, match_rate DESC, j.site ASC
            """

    return execute_query_search(query, {"search_terms": search_terms})


if __name__ == '__main__':
    print("Nothing to Test...")

    # --- TESTING DATABASE ---
    # shutdown_neo4j()
    # add_label('aaleniano', d.NOT_FOUND_IN_WEB)

    database_connection_test()
    # print(neo4j_path)
