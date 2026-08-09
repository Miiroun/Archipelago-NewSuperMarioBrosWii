from abc import ABC, abstractmethod
from typing import List

from wiithon.disc.structs.certificate import Certificate
from wiithon.disc.structs.disc_header import DiscHeader
from wiithon.disc.structs.tmd import TMD
from wiithon.disc.structs.ticket import Ticket
from wiithon.fst.tree import FST


class PartitionSource(ABC):
    @abstractmethod
    def get_partition_type(self) -> int: pass
    
    @abstractmethod
    def get_tmd(self) -> TMD: pass
    
    @abstractmethod
    def get_certificates(self) -> List[Certificate]: pass
    
    @abstractmethod
    def get_encrypted_header(self) -> DiscHeader: pass
    
    @abstractmethod
    def get_bi2(self) -> bytes: pass
    
    @abstractmethod
    def get_apploader(self) -> bytes: pass
    
    @abstractmethod
    def get_dol(self) -> bytes: pass
    
    @abstractmethod
    def get_fst(self) -> FST: pass
    
    @abstractmethod
    def get_ticket(self) -> Ticket: pass
    
    @abstractmethod
    def get_file_data(self, path: List[str]) -> bytes: pass
