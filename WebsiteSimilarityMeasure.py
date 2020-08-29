from zss import simple_distance, Node
from bs4 import BeautifulSoup
from lxml import html
from lxml import etree
import apted
import config
import lxml
import bs4
import re
import os
import json
import datetime


class TreeNode(object):
    def __init__(self, name, children=None):
        self.name = name
        self.children = children or list()

    @staticmethod
    def get_children(node):
        return node.children

    @staticmethod
    def get_name(node):
        return node.name

    def addkid(self, node, before=False):
        if before:  self.children.insert(0, node)
        else:   self.children.append(node)
        return self


class DomTreeSimilarityApted(object):
    def __init__(self, html_file1, html_file2):
        self.tree1_count = 0
        self.tree2_count = 0
        self.html_file1 = html_file1
        self.html_file2 = html_file2

    def construct_dom_tree(self, tree_node, parent_node, soup, flag):
        parent_node.addkid(tree_node)
        for child_soup in soup.children:
            if not isinstance(child_soup, bs4.element.Tag):
                continue
            if child_soup.name == 'script' or child_soup.name == 'meta' or child_soup.name == 'link':
                continue
            child_node = TreeNode(child_soup.name)
            if flag:
                self.tree1_count += 1
            else:
                self.tree2_count += 1
            self.construct_dom_tree(child_node, tree_node, child_soup, flag)
        return tree_node

    def run(self):
        with open('ICO_Sanitized_Htmls/' + self.html_file1, 'r', encoding='utf-8') as f:
            unparsed_html_1 = f.read()
        with open('ICO_Sanitized_Htmls/' + self.html_file2, 'r', encoding='utf-8') as f:
            unparsed_html_2 = f.read()
        root = TreeNode('root')
        soup_1 = BeautifulSoup(unparsed_html_1, 'lxml')
        soup_2 = BeautifulSoup(unparsed_html_2, 'lxml')
        for content in soup_1.contents:
            if isinstance(content, bs4.element.Tag):
                soup_1 = content
        for content in soup_2.contents:
            if isinstance(content, bs4.element.Tag):
                soup_2 = content
        dom_tree_1 = self.construct_dom_tree(TreeNode(soup_1.name), root, soup_1, True)
        dom_tree_2 = self.construct_dom_tree(TreeNode(soup_2.name), root, soup_2, False)
        tree_distance = apted.APTED(dom_tree_1, dom_tree_2)
        dom_tree_similarity = 1 - abs(tree_distance.compute_edit_distance()/(self.tree1_count+self.tree2_count))
        return dom_tree_similarity


class DomTreeSimilarityZss(object):
    def __init__(self, html_file1, html_file2):
        self.tree1_count = 0
        self.tree2_count = 0
        self.html_file1 = html_file1
        self.html_file2 = html_file2

    def construct_dom_tree(self, tree_node, parent_node, soup, flag):
        parent_node.addkid(tree_node)
        for child_soup in soup.children:
            if not isinstance(child_soup, bs4.element.Tag):
                continue
            if child_soup.name == 'script' or child_soup.name == 'meta' or child_soup.name == 'link':
                continue
            child_node = Node(child_soup.name)
            if flag:
                self.tree1_count += 1
            else:
                self.tree2_count += 1
            self.construct_dom_tree(child_node, tree_node, child_soup, flag)
        return tree_node

    def run(self):
        with open('ICO_Sanitized_Htmls/' + self.html_file1, 'r', encoding='utf-8') as f:
            unparsed_html_1 = f.read()
        with open('ICO_Sanitized_Htmls/' + self.html_file2, 'r', encoding='utf-8') as f:
            unparsed_html_2 = f.read()
        root = Node('root')
        soup_1 = BeautifulSoup(unparsed_html_1, 'lxml')
        soup_2 = BeautifulSoup(unparsed_html_2, 'lxml')
        for content in soup_1.contents:
            if isinstance(content, bs4.element.Tag):
                soup_1 = content
        for content in soup_2.contents:
            if isinstance(content, bs4.element.Tag):
                soup_2 = content
        dom_tree_1 = self.construct_dom_tree(Node(soup_1.name), root, soup_1, True)
        dom_tree_2 = self.construct_dom_tree(Node(soup_2.name), root, soup_2, False)
        tree_distance = simple_distance(dom_tree_1, dom_tree_2)
        dom_tree_similarity = 1 - abs(tree_distance/(self.tree1_count+self.tree2_count)) * 1.0
        return dom_tree_similarity


class LongestCommonTagSubsequence(object):
    def __init__(self, html_file1, html_file2):
        self.tag_sequence_1 = None
        self.tag_sequence_2 = None
        self.html_file1 = html_file1
        self.html_file2 = html_file2

    def construct_tag_sequence(self, _etree):
        tag_sequence = []

        for _tag in _etree.getroot().iter():
            if _tag.tag == "script" or _tag.tag == "meta" or _tag.tag == "link" or _tag.tag == "style":
                continue
            if isinstance(_tag, html.HtmlElement):
                tag_sequence.append(_tag.tag)
        return tag_sequence

    def compute_lcts(self):
        len1 = len(self.tag_sequence_1)
        len2 = len(self.tag_sequence_2)
        res = [[0 for i in range(len1 + 1)] for j in range(len2 + 1)]
        for i in range(1, len2 + 1):
            for j in range(1, len1 + 1):
                if self.tag_sequence_2[i - 1] == self.tag_sequence_1[j - 1]:
                    res[i][j] = res[i - 1][j - 1] + 1
                else:
                    res[i][j] = max(res[i - 1][j], res[i][j - 1])
        return res[-1][-1]

    def run(self):
        etree_1 = html.parse('ICO_Sanitized_Htmls/' + self.html_file1)
        etree_2 = html.parse('ICO_Sanitized_Htmls/' + self.html_file2)
        self.tag_sequence_1 = self.construct_tag_sequence(etree_1)
        self.tag_sequence_2 = self.construct_tag_sequence(etree_2)
        lcts = self.compute_lcts()
        lcts_similarity = 2.0 * lcts / (len(self.tag_sequence_1) + len(self.tag_sequence_2))
        return lcts_similarity


class HtmlStructuralSimilarity(object):
    def __init__(self, html_file1, html_file2):
        self.html_file1 = html_file1
        self.html_file2 = html_file2

    def get_html_structure_similarity(self):
        if config.quick_mode:
            dom_tree_similarity_instance = DomTreeSimilarityApted(self.html_file1, self.html_file2)
        else:
            dom_tree_similarity_instance = DomTreeSimilarityZss(self.html_file1, self.html_file2)
        lcts_similarity_instance = LongestCommonTagSubsequence(self.html_file1, self.html_file2)
        #starttime = datetime.datetime.now()
        dom_tree_similarity = dom_tree_similarity_instance.run()
        #endtime = datetime.datetime.now()
        #print('tree edit distance runtime:'+ str(endtime - starttime))
        #print('dom similarity:' + str(dom_tree_similarity))

        #starttime = datetime.datetime.now()
        lcts_similarity = lcts_similarity_instance.run()
        #endtime = datetime.datetime.now()
        #print('lcts runtime:' + str(endtime - starttime))
        #print('lcts similarity:' + str(lcts_similarity))
        return float((dom_tree_similarity + lcts_similarity)/2) * 100


class CssSimilarity(object):
    def __init__(self, html_file1, html_file2):
        self.html_file1 = html_file1
        self.html_file2 = html_file2
        self.set1 = None
        self.set2 = None

    def get_css_list(self, _etree):
        classes = set(_etree.xpath('//*[@class]/@class'))
        ids = set(_etree.xpath('//*[@id]/@id'))
        result_set = set()
        for _class in classes:
            for __class in _class.split():
                result_set.add(__class)
        for _id in ids:
            for __id in _id.split():
                result_set.add(__id)
        return result_set

    def jaccard_coefficient(self):
        intersection = 0
        for i in self.set1:
            if i in self.set2:
                intersection = intersection + 1

        denominator = len(self.set1) + len(self.set2) - intersection
        return float(intersection / denominator)

    def run(self):
        with open('ICO_Sanitized_Htmls/' + self.html_file1, 'r', encoding='utf-8') as f:
            unparsed_html_1 = f.read()
        with open('ICO_Sanitized_Htmls/' + self.html_file2, 'r', encoding='utf-8') as f:
            unparsed_html_2 = f.read()
        etree1 = etree.HTML(unparsed_html_1)
        etree2 = etree.HTML(unparsed_html_2)
        self.set1 = self.get_css_list(etree1)
        self.set2 = self.get_css_list(etree2)
        return self.jaccard_coefficient() * 100


class JsSimilarity(object):
    def __init__(self, html_file1, html_file2):
        self.html_file1 = html_file1
        self.html_file2 = html_file2
        self.set1 = None
        self.set2 = None

    def get_js_list(self, _etree):
        scripts = set(_etree.xpath('//script/@src'))
        result_set = set()
        pattern = re.compile("(?<=\/)[^\/]+(?=\.js)")
        for script in scripts:
            try:
                if not script:
                    continue
                _script = pattern.search(script).group()
                result_set.add(_script)
            except Exception as e:
                print(e)
        return result_set

    def jaccard_coefficient(self):
        intersection = 0
        for i in self.set1:
            if i in self.set2:
                intersection = intersection + 1

        denominator = len(self.set1) + len(self.set2) - intersection
        return float(intersection / denominator) * 100

    def run(self):
        with open('ICO_Sanitized_Htmls/' + self.html_file1, 'r', encoding='utf-8') as f:
            unparsed_html_1 = f.read()
        with open('ICO_Sanitized_Htmls/' + self.html_file2, 'r', encoding='utf-8') as f:
            unparsed_html_2 = f.read()
        etree1 = etree.HTML(unparsed_html_1)
        etree2 = etree.HTML(unparsed_html_2)
        self.set1 = self.get_js_list(etree1)
        self.set2 = self.get_js_list(etree2)
        return self.jaccard_coefficient()


class BackendSimilarity(object):
    def __init__(self, html_file1, html_file2, tech_list):
        self.html_file1 = html_file1
        self.html_file2 = html_file2
        self.tech_list = tech_list
        self.list1= None
        self.list2 = None

    def get_backend_tech_stack(self):
        ico_name_1 = self.html_file1.replace('.html', '')
        ico_name_2 = self.html_file2.replace('.html', '')
        tech_stack_1 = None
        tech_stack_2 = None
        for tech in self.tech_list:
            if tech['ICO name'] == ico_name_1:
                tech_stack_1 = tech['Tech Profile']
            if tech['ICO name'] == ico_name_2:
                tech_stack_2 = tech['Tech Profile']
        return tech_stack_1, tech_stack_2

    def jaccard_coefficient(self):
        set1 = set(self.list1)
        set2 = set(self.list2)
        intersection = 0
        for i in set1:
            if i in set2:
                intersection = intersection + 1

        denominator = len(set1) + len(set2) - intersection
        return float(intersection / denominator)

    def run(self):
        self.list1, self.list2 = self.get_backend_tech_stack()
        if self.list1 == None or self.list2 == None:
            return 0
        return self.jaccard_coefficient() * 100


class WebsiteSimilarityMeasure(object):
    @staticmethod
    def convert_to_similarity_matrix():
        with open('website_pairwise_similarity.json', 'r') as f:
            init_data = json.load(f)

        html_file_dir = './ICO_Sanitized_Htmls'
        html_files = os.listdir(html_file_dir)
        total_num = len(html_files)
        cols = rows = total_num
        similarity_matrix = [[0 for col in range(cols)] for row in range(rows)]

        index = 0
        for i in range(rows):
            similarity_matrix[i][i] = 100
            for j in range(i + 1, cols):
                similarity_matrix[i][j] = init_data[index]['similarity']
                similarity_matrix[j][i] = init_data[index]['similarity']
                index = index + 1

        data_str = json.dumps(similarity_matrix, indent=4)
        with open('similarity_matrix.json', 'w') as f:
            f.write(data_str)

    @staticmethod
    def run():
        html_file_dir = './ICO_Sanitized_Htmls'
        html_files = os.listdir(html_file_dir)
        backend_tech_stack_path = 'SanitizedIcoBackendStackList.json'
        with open(backend_tech_stack_path, 'r') as f:
            backend_tech_stack_list = json.load(f)
        total_files_cnt = len(html_files)
        result_list = list()
        failed_list = list()
        for i in range(0, total_files_cnt):
            print('Calculating on %s (%d/%d)' % (html_files[i], i + 1, total_files_cnt))
            for j in range(i + 1, total_files_cnt):
                try:
                    html_structure_similarity = HtmlStructuralSimilarity(html_files[i], html_files[j])
                    html_structure_similarity_value = html_structure_similarity.get_html_structure_similarity()
                    #print('html structure similarity:' + str(html_structure_similarity_value))

                    css_similarity = CssSimilarity(html_files[i], html_files[j])
                    css_similarity_value = css_similarity.run()
                    #print('css similarity:' + str(css_similarity_value))

                    js_similarity = JsSimilarity(html_files[i], html_files[j])
                    js_similarity_value = js_similarity.run()
                    #print('js similarity:' + str(js_similarity_value))

                    backend_similarity = BackendSimilarity(html_files[i], html_files[j], backend_tech_stack_list)
                    backend_similarity_value = backend_similarity.run()
                    #print('backend similarity:' + str(backend_similarity_value))

                    website_similarity = max(float(html_structure_similarity_value),
                                             float(css_similarity_value),
                                             float(js_similarity_value),
                                             0.8 * backend_similarity_value)
                    #print('website similarity:' + str(website_similarity))

                    result_list.append({
                        'ICO name 1': html_files[i],
                        'ICO name 2': html_files[j],
                        'similarity': website_similarity
                    })
                except Exception as e:
                    print(e)
                    failed_list.append((html_files[i], html_files[j]))

            if (i+1) % 100 == 0:
                with open('./temporary_pairwise_similarity/website_pairwise_similarity-'
                          + html_files[i][:-5]
                          + '.json', 'w') as json_out:
                    json.dump(result_list, json_out, indent=4)

        with open('website_pairwise_similarity.json', 'w') as json_out:
            json.dump(result_list, json_out, indent=4)

        with open('failed_website_similarity.json', 'w') as json_out:
            json.dump(result_list, json_out, indent=4)

if __name__ == "__main__":
    WebsiteSimilarityMeasure.run()
    WebsiteSimilarityMeasure.convert_to_similarity_matrix()


