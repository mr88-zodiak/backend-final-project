import gensim.downloader as api
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


model = api.load("glove-wiki-gigaword-100")

def embed_sentence(sentence):
    words = [w for w in sentence.lower().split() if w in model]
    if not words:
        return np.zeros(model.vector_size)
    return np.mean([model[w] for w in words], axis=0)

riwayat_donasi = ["motor", "tas bekas", "laptop bekas", "baju bekas"]
kebutuhan_pengguna = ["laptop bekas", "motor bekas", "tas bekas", "sofa"]


vec_donasi = [embed_sentence(s) for s in riwayat_donasi]
vec_kebutuhan = [embed_sentence(s) for s in kebutuhan_pengguna]


similarity_matrix = cosine_similarity(vec_donasi, vec_kebutuhan)

import pandas as pd
df = pd.DataFrame(similarity_matrix, index=riwayat_donasi, columns=kebutuhan_pengguna)
print(df)
