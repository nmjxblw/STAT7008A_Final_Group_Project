query = 'what is mamba in ai?'
#query = 'find the paper about mamba.'

from .answer_generator import Generator
A = Generator()
query_type, reference = A.set_demand(query)
ref_id = [ref[0] for ref in reference]
reply = A.get_LLM_reply(ref_id)

print(query_type)
print(reference)
print(A._prompt)
print(reply)
