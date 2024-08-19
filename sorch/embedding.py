import torch
import torch.nn.functional as F
from transformers import AutoModel, AutoTokenizer

from sorch.model_utils import get_device

EMBEDDING_MODEL_NAMES = [
    "noinstruct-small-embedding-v0",
]

EmbeddingVector = list[float]

class Embedding:
    def __init__(self, dim: int):
        """Initializes the embedding model.
        
        Args:
            dim (int, optional): The dimension of the embedding vector. Defaults to None.
        """
        self._dim = dim

    @property
    def dim(self):
        """The dimension of the embedding vector."""
        return self._dim

    def embed_document(self, text: str | list[str], chunking_strategy: str) -> EmbeddingVector | list[EmbeddingVector]:
        """Embeds a document or a list of documents."""
        raise NotImplementedError

    def embed_query(self, text: str | list[str], chunking_strategy: str) -> EmbeddingVector | list[EmbeddingVector]:
        """Embeds a query or a list of queries."""
        raise NotImplementedError

class NoInstructEmbedding(Embedding):
    def __init__(self, model_name: str, device: str = "auto"):
        self.device = get_device(device)
        self.model = AutoModel.from_pretrained(model_name).to(device).eval()
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        # Infer model of embedding model based on HuggingFace model config
        super().__init__(dim=self.model.config.hidden_size)
    
    def embed_document(self, text: str | list[str], chunking_strategy: str = "prefix"):
        self.model.eval()
        if chunking_strategy != "prefix":
            raise ValueError(f"chunking_strategy={chunking_strategy} was passed but only `prefix` is supported.")
        
        is_batch = True
        if isinstance(text, str):
            is_batch = False
            text = [text]
        inp = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True).to(self.device)
        with torch.no_grad():
            output = self.model(**inp)
        vectors = output.last_hidden_state[:, 0, :]
        if not is_batch:
            vectors = vectors[0]
        return vectors.tolist()
    
    def embed_query(self, text: str | list[str], chunking_strategy: str = "prefix"):
        self.model.eval()
        if chunking_strategy != "prefix":
            raise ValueError(f"chunking_strategy={chunking_strategy} was passed but only `prefix` is supported.")
        
        is_batch = True
        if isinstance(text, str):
            is_batch = False
            text = [text]
        inp = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True).to(self.device)
        with torch.no_grad():
            output = self.model(**inp)
        vectors = output.last_hidden_state * inp["attention_mask"].unsqueeze(2)
        vectors = vectors.sum(dim=1) / inp["attention_mask"].sum(dim=-1).view(-1, 1)
        if not is_batch:
            vectors = vectors[0]
        return vectors.tolist()

def get_embedding(model_name: str, device: str = "cpu"):
    if model_name == "noinstruct-small-embedding-v0":
        return NoInstructEmbedding("avsolatorio/NoInstruct-small-Embedding-v0", device)
    else:
        raise ValueError(f"model_name={model_name} is not supported.")