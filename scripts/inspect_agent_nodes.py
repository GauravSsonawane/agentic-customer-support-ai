import importlib

def main():
    m = importlib.import_module('app.agent_nodes')
    print('answer_question' in m.__dict__)
    print([k for k in m.__dict__.keys() if 'answer' in k.lower()])
    print('analyze_node' in m.__dict__)
    print(m.analyze_node)

if __name__ == '__main__':
    main()
